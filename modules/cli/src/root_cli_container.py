"""Root: CLI feature DI container."""

from __future__ import annotations

from .capabilities_cli_process import CliProcessCapability
from .surface_close_command import handle as close_handle
from .surface_init_command import handle as init_handle
from .surface_render_command import handle as render_handle
from .surface_run_command import handle as run_handle
from .surface_screenshot_command import handle as screenshot_handle
from .surface_status_command import handle as status_handle

_handles = (
    close_handle,
    init_handle,
    render_handle,
    run_handle,
    screenshot_handle,
    status_handle,
)


class CliContainer:
    """Dependency injection container for CLI feature."""

    def __init__(self) -> None:
        self._process_capability = CliProcessCapability()

    @property
    def process_capability(self) -> CliProcessCapability:
        return self._process_capability
