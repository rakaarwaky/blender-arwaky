"""CLI close command — Close active Blender instance."""

from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.cli.utility_cli_process import is_running, kill_blender
from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object, _dispatcher: object | None = None) -> dict[str, object]:
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

    if pid and is_running(pid).success:
        kill_blender(pid)

    registry.clear()

    if save_failed:
        return {
            "success": True,
            "message": "Blender closed (save may have failed)",
            "warnings": ["File may not have been saved before close"],
        }
    return {"success": True, "message": "Blender closed"}
