"""CLI run command — Execute any action on active Blender via socket."""

import json

from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS
from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient


def _flatten_schemas() -> dict[str, dict[str, object]]:
    """Flatten domain-grouped schemas into action_name → schema lookup."""
    flat: dict[str, dict[str, object]] = {}
    for domain_actions in DISPATCHER_ACTION_SCHEMAS.values():
        flat.update(domain_actions)
    return flat


_ALL_ACTIONS = _flatten_schemas()


def _get_action_schema(action: str) -> dict[str, object] | None:
    return _ALL_ACTIONS.get(action)


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object, dispatcher: object | None = None) -> dict[str, object]:
    """Handle run command through Dispatcher when injected, else socket fallback."""
    action = args.action
    params = args.params if isinstance(args.params, dict) else json.loads(args.params)

    schema = _get_action_schema(action)
    if schema is None:
        all_names = "\n".join(sorted(_ALL_ACTIONS.keys()))
        return _mask_error("validation_error", "cli-400", f"Unknown action: {action}. Available: {all_names}")

    if dispatcher is not None:
        try:
            request = ActionCommandVO(
                action_name=action,
                parameters=params,
                confirmation_flag=bool(getattr(args, "confirm", False) or getattr(args, "force", False)),
            )
            envelope = dispatcher.execute_action(request)
            if envelope.success:
                return {
                    "success": True,
                    "result": envelope.data,
                    "tracking_id": envelope.tracking_id,
                    "warnings": envelope.warnings,
                    "metadata": envelope.metadata,
                }
            raw_category = envelope.error_category or "upstream"
            category = str(getattr(raw_category, "value", raw_category))
            if category.startswith("DispatchErrorCategory."):
                category = category.rsplit(".", 1)[-1].lower()
            return _mask_error(category, "cli-502")
        except Exception:
            return _mask_error("unexpected", "cli-500")

    registry = Registry()
    error = registry.assert_active(args.filepath)
    if error:
        return _mask_error("state", "cli-409", error)

    port = registry.get_port()
    try:
        with BlenderSocketClient(port=port) as client:
            response = client.send_command(action, params)
            if response.get("status") == "success":
                return {"success": True, "result": response.get("result")}
            return _mask_error("upstream", "cli-502", response.get("message", "Blender command failed"))
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")
