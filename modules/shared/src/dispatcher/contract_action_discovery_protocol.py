"""Dispatcher domain contract: action discovery protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-002: Discover Actions
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_discovery_result_vo import DiscoveryResultVO


class ActionDiscoveryProtocol(ABC):
    """Protocol for discovering and listing registered actions."""

    @abstractmethod
    def discover_actions(
        self,
        name_filter: str | None = None,
        capability_filter: str | None = None,
        detail_level: str = "standard",
    ) -> DiscoveryResultVO:
        """Discover actions from the catalog with optional filtering.

        FR-DSP-002: Returns canonical shape to all consumers.
        Filter matching nothing returns empty list, not error.
        """
        ...
