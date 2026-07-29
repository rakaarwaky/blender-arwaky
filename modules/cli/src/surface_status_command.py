"""CLI status command — Show active Blender status."""

from typing import Any

from modules.shared.src.launcher.utility_blender_process import is_running
from modules.shared.src.launcher.utility_runtime_registry import Registry


def handle(_args: Any) -> dict[str, Any]:
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
