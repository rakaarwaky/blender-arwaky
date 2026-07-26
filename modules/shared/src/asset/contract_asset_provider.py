"""Asset provider domain contract: asset provider port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import AssetId

from .taxonomy_asset_data_vo import AssetMetadata
from .taxonomy_asset_vo import AssetDownloadVO, AssetSearchVO


class AssetProviderPort(ABC):
    """Port interface for asset provider services."""

    @abstractmethod
    async def search_assets(self, request: AssetSearchVO) -> AssetSearchVO:
        """Search for assets matching the query."""
        ...

    @abstractmethod
    async def get_asset_details(self, asset_id: AssetId) -> AssetMetadata | None:
        """Get detailed metadata for a specific asset."""
        ...

    @abstractmethod
    async def download_asset(self, request: AssetDownloadVO) -> AssetDownloadVO:
        """Download an asset to the specified destination."""
        ...