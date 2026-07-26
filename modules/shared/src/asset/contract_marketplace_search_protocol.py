"""Asset domain contract: marketplace search protocol (ABC based).

Defines the protocol for searching downloadable 3D models from marketplaces.
AES Contract layer — pure ABC definitions, no implementation.

FR-AST-005: Search Downloadable Model Marketplaces
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_asset_vo import AssetSearchVO


class MarketplaceSearchProtocol(ABC):
    """Protocol for searching downloadable model marketplaces."""

    @abstractmethod
    async def search_marketplace_models(
        self,
        query: str,
        categories: list[str] | None = None,
        downloadable_only: bool = True,
        page_token: str | None = None,
    ) -> AssetSearchVO:
        """Search online model marketplaces for downloadable models.

        FR-AST-005: Filters out non-downloadable models by default.
        Normalizes marketplace response into standard asset metadata format.
        Uses configured authentication credentials when required.
        """
        pass