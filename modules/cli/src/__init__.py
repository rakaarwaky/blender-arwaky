"""CLI surface — Blender process management, commands, registry, and socket client."""

from .surface_cli_blender_manager import (
    find_blender,
    launch_blender,
    kill_blender,
    is_running,
)
from .surface_cli_commands import (
    close,
    init,
    render,
    run,
    screenshot,
    status,
)
from .surface_cli_main import main
from .surface_cli_registry import Registry, RegistryState
from .surface_cli_socket_client import BlenderSocketClient

__all__ = [
    "RegistryState",
    "Registry",
    "BlenderSocketClient",
    "find_blender",
    "launch_blender",
    "kill_blender",
    "is_running",
    "init",
    "run",
    "screenshot",
    "render",
    "close",
    "status",
    "main",
]
