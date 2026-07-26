"""Dispatcher domain contract: action catalog registration protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-001: Register Action Catalog
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_action_metadata_vo import ActionMetadataVO


class CatalogRegistrationProtocol(ABC):
    """Protocol for registering actions into the dispatcher catalog."""

    @abstractmethod
    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO:
        """Register an action in the catalog. Returns enriched metadata with catalog version.

        FR-DSP-001: Duplicate names are rejected or replaced per policy.
        Catalog exposes deterministic ordering sorted by action name.
        """
        pass
