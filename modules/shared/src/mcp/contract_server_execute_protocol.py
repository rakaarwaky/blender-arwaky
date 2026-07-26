"""MCP domain contract: server execution protocol (ABC based).

Defines the protocol for executing 3D actions via the CLI environment.

FR-MCP-002: Execute 3D Action
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ServerExecuteProtocol(ABC):
    """Protocol for executing 3D actions via CLI environment."""

    @abstractmethod
    async def execute_action(self, action: str, params: dict | None = None) -> dict:
        """Execute a 3D action with 1:1 CLI parity.

        FR-MCP-002: Translates AI request to exact CLI instruction.
        Enforces same constraints, priority, and sequential processing as CLI.
        Returns structured result with success status, data, or error details.
        """
        pass