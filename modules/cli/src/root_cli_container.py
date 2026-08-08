"""Root: CLI feature DI container."""

from __future__ import annotations

from . import (
    surface_close_command,
    surface_init_command,
    surface_render_command,
    surface_run_command,
    surface_screenshot_command,
    surface_status_command,
)

_handles = (
    surface_close_command.handle,
    surface_init_command.handle,
    surface_render_command.handle,
    surface_run_command.handle,
    surface_screenshot_command.handle,
    surface_status_command.handle,
)


class CliContainer:
    """Dependency injection container for CLI feature."""
