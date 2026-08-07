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
from .capabilities_cli_process import CliProcessCapability

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

    def __init__(self) -> None:
        self._process_capability = CliProcessCapability()

    @property
    def process_capability(self) -> CliProcessCapability:
        return self._process_capability
