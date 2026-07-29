"""CLI run command — Execute any action on active Blender via socket."""

import json
from typing import Any

from modules.dispatcher.src.surface_action_registry import ALL_ACTIONS, get_action_schema
from .utility_cli_registry import Registry
from .utility_cli_socket_client import BlenderSocketClient


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, Any]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: Any) -> dict[str, Any]:
    """Handle run command: execute any action by name on active Blender."""
    action = args.action
    params = args.params if isinstance(args.params, dict) else json.loads(args.params)

    schema = get_action_schema(action)
    if schema is None:
        all_names = "\n".join(sorted(ALL_ACTIONS.keys()))
        return _mask_error("validation_error", "cli-400", f"Unknown action: {action}. Available: {all_names}")

    registry = Registry()
    error = registry.assert_active(args.filepath)
    if error:
        return _mask_error("state", "cli-409", error)

    port = registry.get_port()
    try:
        with BlenderSocketClient(port=port) as client:
            result = client.send_command(action, params)
            return result
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")
