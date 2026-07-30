"""CLI status command — Show active Blender status."""


from modules.shared.src.cli.utility_cli_process import is_running
from modules.shared.src.cli.utility_cli_registry import Registry


def handle(_args: object) -> dict[str, object]:
    """Handle status command: show active Blender instance status."""
    registry = Registry()

    if not registry.is_active():
        return {"success": True, "active": False, "message": "No Blender instance is active"}

    return {
        "success": True,
        "active": True,
        "running": registry.get_pid() is not None and is_running(registry.get_pid()),
        "filepath": registry.get_active(),
        "pid": registry.get_pid(),
        "port": registry.get_port(),
    }
