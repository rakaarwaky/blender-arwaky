"""
Dispatcher: Route MCP actions to AgentOrchestrator.

This capability is the sole entry point for executing any BlenderArwaky action.
Handlers (MCP tools, CLI) delegate here — they contain no business logic.
"""

import asyncio
import inspect
import json
import logging
import re
import typing
from typing import Any

from pydantic import BaseModel

from ..common.contract_execute_action_protocol import ExecuteActionProtocol
from ..common.taxonomy_core_vo import ActionName, Details, Prompt
from ..common.taxonomy_command_catalog_constant import CommandCatalog

logger = logging.getLogger("BlenderMCPServer")

# Validation constants
MAX_ACTION_NAME_LENGTH = 100
MAX_STRING_ARG_LENGTH = 50_000
ACTION_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

# Dispatch timeout (seconds) — prevents stuck Blender calls from blocking the server
DISPATCH_TIMEOUT_S: float = 30.0

# Protocol name → orchestrator attribute mapping (Open/Closed: add new entries here)
_PROTOCOL_ATTR: dict[str, str] = {
    "BlenderPort": "blender",
    "SceneOperateProtocol": "operate_scene_capability",
    "AssetSearchProtocol": "search_asset_capability",
    "AssetProviderPort": "search_asset_capability",
    "ObjectOperateProtocol": "object_operate_capability",
    "RenderOperateProtocol": "render_operate_capability",
    "ImportExportProtocol": "import_export_capability",
}


def _unwrap_annotation(annotation: Any) -> Any | None:
    """Unwrap Optional/Annotated/Union type hints to get the underlying type."""
    if annotation is inspect.Parameter.empty:
        return None

    origin = typing.get_origin(annotation)
    if origin is None:
        # Plain type (e.g. GetScreenshotRequestVO)
        return annotation if isinstance(annotation, type) else None

    # Handle Optional[X] (Union[X, None]) and Annotated[X, ...]
    if origin is typing.Union:
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        return args[0] if len(args) == 1 and isinstance(args[0], type) else None

    # Annotated[X, metadata] — return the first arg
    if origin is typing.Annotated:
        args = typing.get_args(annotation)
        return args[0] if args and isinstance(args[0], type) else None

    return None


class ActionExecuteActions(ExecuteActionProtocol):
    """Dispatches actions to the orchestrator based on COMMAND_CATALOG."""

    def __init__(self, orchestrator: Any):
        self._orch = orchestrator
        self._sig_cache: dict[Any, inspect.Signature] = {}

    async def execute(self, action: ActionName, args: Details | None = None) -> Prompt:
        """Execute an action via the orchestrator.

        Args:
            action: Action name (key in COMMAND_CATALOG)
            args: Arguments dict for the action

        Returns:
            JSON string result (pydantic model dumped) or plain text wrapped in Prompt
        """
        args = args or {}

        if err := self._validate_action_name(str(action)):
            return Prompt(err)
        if not isinstance(args, dict):
            return Prompt(f"Error: 'args' must be a dict, got {type(args).__name__}.")

        spec = CommandCatalog.COMMAND_CATALOG.get(str(action))
        if spec is None:
            return Prompt(f"Error: Unknown action '{action}'. Use list_commands() to discover.")

        cap_ref = spec.get("capability")
        if not cap_ref or "." not in cap_ref:
            return Prompt(f"Error: Malformed capability ref for action '{action}'.")

        protocol_name, method_name = cap_ref.rsplit(".", 1)

        cap = self._resolve_capability(protocol_name)
        if cap is None:
            return Prompt(f"Error: No capability for protocol '{protocol_name}' (action '{action}').")

        method = getattr(cap, method_name, None)
        if method is None:
            return Prompt(f"Error: '{protocol_name}' has no method '{method_name}' (action '{action}').")

        args = self._sanitize_args(args)

        logger.info(
            "dispatch action=%s protocol=%s method=%s args_keys=%s", action, protocol_name, method_name, list(args)
        )

        try:
            raw = self._invoke(method, args)
            result = await asyncio.wait_for(raw, timeout=DISPATCH_TIMEOUT_S) if asyncio.iscoroutine(raw) else raw
        except asyncio.TimeoutError:
            logger.warning("action=%s timed out after %ss", action, DISPATCH_TIMEOUT_S)
            return Prompt(json.dumps({"error": "timeout", "action": str(action)}))
        except Exception as e:
            logger.exception("action=%s failed", action)
            return Prompt(json.dumps({"error": str(e), "action": str(action)}, indent=2))

        return Prompt(self._serialize(result))

    def _resolve_capability(self, protocol_name: str) -> Any | None:
        """Resolve capability from the orchestrator via protocol→attribute mapping."""
        attr = _PROTOCOL_ATTR.get(protocol_name)
        if attr is None:
            return None
        return getattr(self._orch, attr, None)

    def _invoke(self, method: Any, args: dict[str, Any]) -> Any:
        """Invoke a capability method, auto-constructing RequestVO when needed.

        Protocol methods expecting a typed RequestVO (pydantic BaseModel) as their
        first parameter receive a constructed instance. Methods with direct scalar
        parameters receive unpacked kwargs.
        """
        sig = self._sig_cache.get(id(method))
        if sig is None:
            sig = inspect.signature(method)
            self._sig_cache[id(method)] = sig

        params = list(sig.parameters.values())

        if params:
            first = params[0]
            unwrapped = _unwrap_annotation(first.annotation)
            if unwrapped is not None and issubclass(unwrapped, BaseModel):
                return method(unwrapped(**args))

        return method(**args)

    def _serialize(self, result: Any) -> str:
        """Serialize capability method execution result to JSON or string."""
        if hasattr(result, "model_dump_json"):
            return result.model_dump_json(indent=2)
        if isinstance(result, dict):
            return json.dumps(result, indent=2, default=str)
        return str(result)

    @staticmethod
    def _validate_action_name(action: str) -> str | None:
        """Validate action name format. Returns error message or None."""
        if not action or not action.strip():
            return "Error: Action name cannot be empty."
        if len(action) > MAX_ACTION_NAME_LENGTH:
            return f"Error: Action name exceeds {MAX_ACTION_NAME_LENGTH} characters."
        if not ACTION_NAME_PATTERN.match(action):
            return (
                f"Error: Invalid action name '{action}'. "
                f"Must be lowercase alphanumeric with underscores (e.g. 'get_scene_info')."
            )
        return None

    @staticmethod
    def _sanitize_args(args: Details) -> Details:
        """Sanitize argument values: strip strings, enforce length limits."""
        sanitized: Details = {}
        for key, value in args.items():
            if isinstance(value, str):
                original_len = len(value)
                value = value.strip()
                if original_len > MAX_STRING_ARG_LENGTH:
                    logger.warning(
                        "Argument '%s' truncated from %d to %d chars",
                        key,
                        original_len,
                        MAX_STRING_ARG_LENGTH,
                    )
                    value = value[:MAX_STRING_ARG_LENGTH]
            sanitized[key] = value
        return sanitized
