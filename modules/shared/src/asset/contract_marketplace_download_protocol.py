"""Asset domain contract: marketplace download protocol (ABC based).

Defines the protocol for downloading models from marketplaces.
AES Contract layer — pure ABC definitions, no implementation.

FR-AST-006: Download from Model Marketplaces
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
)
from .taxonomy_asset_vo import AssetDownloadCacheVO


class MarketplaceDownloadProtocol(ABC):
    """Protocol for downloading models from marketplaces."""

    @abstractmethod
    async def download_marketplace_model(
        self,
        model_id: AssetId,
        destination_policy: str = "unique",
    ) -> AssetDownloadCacheVO:
        """Download a specific 3D model from marketplace.

        FR-AST-006: Downloads strictly into allowed cache directory.
        Safely extracts compressed archives (path traversal prevention).
        Preserves marketplace attribution and license metadata.
        """
        pass