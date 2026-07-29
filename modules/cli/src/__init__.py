"""CLI entry — Blender process management, surface commands, and utilities."""

from modules.shared.src.gateway.utility_socket_client import BlenderSocketClient
from modules.shared.src.launcher.utility_blender_process import (
    find_blender,
    is_running,
    kill_blender,
    launch_blender,
)
from modules.shared.src.launcher.utility_runtime_registry import Registry, RegistryState

from .root_cli_main_entry import main
from .surface_close_command import handle as close_handle
from .surface_init_command import handle as init_handle
from .surface_render_command import handle as render_handle
from .surface_run_command import handle as run_handle
from .surface_screenshot_command import handle as screenshot_handle
from .surface_status_command import handle as status_handle

__all__ = [
    "BlenderSocketClient",
    "Registry",
    "RegistryState",
    "close_handle",
    "find_blender",
    "init_handle",
    "is_running",
    "kill_blender",
    "launch_blender",
    "main",
    "render_handle",
    "run_handle",
    "screenshot_handle",
    "status_handle",
]
