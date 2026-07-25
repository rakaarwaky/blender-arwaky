"""Object domain contract: place asset protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import PlaceAssetRequestVO
from .taxonomy_object_result_vo import PlacementResultVO


class PlaceAssetProtocol(ABC):
    """Protocol interface for placing an asset or existing object in the scene."""

    @abstractmethod
    async def place_asset(self, request: PlaceAssetRequestVO) -> PlacementResultVO:
        """Position an existing object or imported asset at target transform.

        FR-OBJ-001: If object_name is provided, place that specific object.
        Otherwise, place currently selected objects (asset import context).
        """
        ...
