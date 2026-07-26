"""Object domain contract: place asset protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import PlaceAssetVO


class PlaceAssetProtocol(ABC):
    """Protocol interface for placing an asset or existing object in the scene."""

    @abstractmethod
    async def place_asset(self, request: PlaceAssetVO) -> PlaceAssetVO:
        """Position an existing object or imported asset at target transform."""
        ...
