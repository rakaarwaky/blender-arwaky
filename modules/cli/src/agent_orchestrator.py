"""Agent: CLI feature orchestrator.

Coordinates Blender process lifecycle — init, launch, status, close — through
the CliLifecycleProtocol capability layer.
"""

from __future__ import annotations

import logging

from modules.shared.src.cli.contract_cli_aggregate import CliLifecycleProtocol

logger = logging.getLogger("BlenderMCPServer")


class CliOrchestrator:
    """Orchestrates Blender CLI operations via capability protocol."""

    def __init__(self, lifecycle: CliLifecycleProtocol) -> None:
        """Initialize with a CLI lifecycle capability.

        Args:
            lifecycle: A callable or capability that manages Blender lifecycle.
        """
        self._lifecycle = lifecycle

    async def init(self, path: str | None = None) -> dict:
        """Register Blender executable path."""
        return await self._lifecycle.locate_and_register(path)

    async def run(self, extra_args: list[str] | None = None) -> dict:
        """Launch Blender process."""
        return await self._lifecycle.launch(extra_args)

    async def close(self) -> dict:
        """Terminate Blender process."""
        return await self._lifecycle.shutdown()

    async def status(self) -> dict:
        """Check Blender instance status."""
        return await self._lifecycle.check_status()
