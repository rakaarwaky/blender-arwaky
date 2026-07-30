"""CLI entry — Blender process management, commands, and utilities."""

from modules.shared.src.gateway.utility_socket_client import BlenderSocketClient

from .root_cli_main_entry import main
from .utility_cli_process import (
    find_blender,
    is_running,
    kill_blender,
    launch_blender,
)
from .utility_cli_registry import Registry, RegistryState

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

# Command handlers — imported from cmd_* modules for module-level access
from . import cmd_close, cmd_init, cmd_render, cmd_run, cmd_screenshot, cmd_status

close_handle = cmd_close.handle
init_handle = cmd_init.handle
render_handle = cmd_render.handle
run_handle = cmd_run.handle
screenshot_handle = cmd_screenshot.handle
status_handle = cmd_status.handle
