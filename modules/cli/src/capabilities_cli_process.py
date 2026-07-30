"""Capability: CLI process management."""

from __future__ import annotations

from modules.shared.src.cli.contract_cli_process_protocol import ICliProcessProtocol
from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.cli.utility_cli_process import is_running
from modules.shared.src.cli.utility_cli_registry import Registry

_ = Registry


class CliProcessCapability(ICliProcessProtocol):
    """Capability for managing Blender CLI process lifecycle."""

    async def is_process_running(self, pid: int) -> CliResultVo:
        """Check if process is running."""
        running = is_running(pid)
        return CliResultVo(success=True, message=str(running))
