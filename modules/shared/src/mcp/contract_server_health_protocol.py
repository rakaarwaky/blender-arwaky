"""MCP domain contract: server health protocol (ABC based).

Defines the protocol for reporting system health and retrieving configuration.

FR-MCP-005: Report System Health
FR-MCP-006: Retrieve System Configuration
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ServerHealthProtocol(ABC):
    """Protocol for reporting system health and retrieving configuration."""

    @abstractmethod
    async def check_health(self) -> dict:
        """Report operational status of all critical subsystems.

        FR-MCP-005: Checks integration service, CLI environment, 3D app connectivity,
        and configuration validity. Returns detailed breakdown of each subsystem.
        """
        pass

    @abstractmethod
    async def get_config(self) -> dict:
        """Return current system settings and boundaries.

        FR-MCP-006: Returns exact same configuration state as CLI environment.
        Includes ports, auth status, allowed directories, enabled providers, timeouts.
        Sensitive values are automatically redacted.
        """
        pass