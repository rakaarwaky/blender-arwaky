"""Agent: CLI feature orchestrator.

Coordinates Blender process lifecycle — init, launch, status, close — through
the CliLifecycleProtocol capability layer.
"""

from __future__ import annotations

import logging

from modules.shared.src.cli.contract_cli_aggregate import ICliAggregate
from modules.shared.src.cli.contract_cli_lifecycle_protocol import CliLifecycleProtocol
from modules.shared.src.common.taxonomy_core_vo import ToolName

logger = logging.getLogger("BlenderMCPServer")


class CliOrchestrator(CliLifecycleProtocol, ICliAggregate):
    """Orchestrates Blender CLI operations via capability protocol.

    Implements both the lifecycle protocol and the aggregate interface.
    Delegates to the injected lifecycle capability for actual operations.
    """

    def __init__(self, lifecycle: CliLifecycleProtocol) -> None:
        """Initialize with a CLI lifecycle capability.

        Args:
            lifecycle: A callable or capability that manages Blender lifecycle.
        """
        self._lifecycle = lifecycle

    async def init(self, path: str | None = None, source_tool: ToolName | None = None) -> dict:
        """Register Blender executable path with optional tool tracking."""
        return await self._lifecycle.locate_and_register(path, source_tool)

    async def run(self, extra_args: list[str] | None = None) -> dict:
        """Launch Blender process."""
        return await self._lifecycle.launch(extra_args)

    async def close(self) -> dict:
        """Terminate Blender process."""
        return await self._lifecycle.shutdown()

    async def status(self) -> dict:
        """Check Blender instance status."""
        return await self._lifecycle.check_status()
