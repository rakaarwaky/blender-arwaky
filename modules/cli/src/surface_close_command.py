"""CLI close command — Close active Blender instance."""

from typing import Any

from modules.shared.src.gateway.utility_socket_client import BlenderSocketClient

from .utility_cli_process import is_running, kill_blender
from .utility_cli_registry import Registry


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, Any]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: Any) -> dict[str, Any]:
    """Handle close command: close active Blender instance."""
    registry = Registry()

    error, port = registry.assert_active(args.filepath), registry.get_port()
    if error:
        return _mask_error("state", "cli-409", error)

    pid = registry.get_pid()
    save_failed = False

    try:
        with BlenderSocketClient(port=port) as client:
            client.send_command("execute_code", {"code": "import bpy\nbpy.ops.wm.save_mainfile()"})
    except Exception:
        save_failed = True

    if pid and is_running(pid):
        kill_blender(pid)

    registry.clear()

    if save_failed:
        return {"success": True, "message": "Blender closed (save may have failed)", "warnings": ["File may not have been saved before close"]}
    return {"success": True, "message": "Blender closed"}
