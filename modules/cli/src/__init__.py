"""CLI entry — Blender process management, commands, and utilities."""

from modules.cli.src.capabilities_cli_registry import Registry
from modules.gateway.src.capabilities_socket_client import BlenderSocketClient
from modules.shared.src.cli.taxonomy_cli_vo import RegistryStateVo as RegistryState
from modules.shared.src.cli.utility_cli_process import (
    find_blender,
    is_running,
    kill_blender,
    launch_blender,
)

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
    "render_handle",
    "run_handle",
    "screenshot_handle",
    "status_handle",
]

# Command handlers — imported from surface_*_command modules for module-level access
from . import (
    surface_close_command,
    surface_init_command,
    surface_render_command,
    surface_run_command,
    surface_screenshot_command,
    surface_status_command,
)

close_handle = surface_close_command.handle
init_handle = surface_init_command.handle
render_handle = surface_render_command.handle
run_handle = surface_run_command.handle
screenshot_handle = surface_screenshot_command.handle
status_handle = surface_status_command.handle
