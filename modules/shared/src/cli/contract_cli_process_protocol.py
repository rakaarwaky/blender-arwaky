"""CLI domain contract: process management protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_cli_vo import CliResultVo


class ICliProcessProtocol(ABC):
    """Protocol for CLI process operations (launch, kill, status)."""

    @abstractmethod
    async def is_process_running(self, pid: int) -> CliResultVo:
        """Check if process is running."""
        ...
