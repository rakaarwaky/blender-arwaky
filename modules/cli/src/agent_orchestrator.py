"""Agent: CLI feature orchestrator.

Coordinates Blender process lifecycle — init, launch, status, close.
"""

import logging
from typing import Any

logger = logging.getLogger("BlenderMCPServer")


class CliOrchestrator:
    """Orchestrates Blender CLI operations."""

    def __init__(self, manager: Any):
        self._manager = manager

    def init(self, path: str | None = None) -> None:
        """Register Blender executable path."""
        self._manager.init_blender(path)

    def run(self, args: list[str] | None = None) -> None:
        """Launch Blender process."""
        self._manager.launch_blender(args)

    def close(self) -> None:
        """Terminate Blender process."""
        self._manager.close_blender()

    def status(self) -> dict:
        """Check Blender instance status."""
        return self._manager.get_status()
