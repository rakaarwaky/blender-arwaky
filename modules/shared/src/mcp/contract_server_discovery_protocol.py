"""MCP domain contract: server discovery protocol (ABC based).

Defines the protocol for discovering available actions and reading skill documentation.

FR-MCP-003: Discover Available Actions
FR-MCP-004: Retrieve Skill Documentation
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ServerDiscoveryProtocol(ABC):
    """Protocol for discovering available actions and reading documentation."""

    @abstractmethod
    async def list_actions(self) -> dict:
        """Return the complete catalog of available 3D actions.

        FR-MCP-003: Returns exact same list available via CLI.
        Each action includes name, description, parameter schema, example, timeout, mutation flag.
        """
        pass

    @abstractmethod
    async def read_skill_context(self, skill_name: str | None = None) -> dict:
        """Return skill documentation content.

        FR-MCP-004: Returns exact same documentation files used by CLI.
        Defaults to root/overview if no skill name provided.
        Returns documentation as readable text (Markdown).
        """
        pass
