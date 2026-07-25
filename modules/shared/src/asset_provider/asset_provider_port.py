"""Asset provider domain contract: asset provider port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import AssetId
from .taxonomy_asset_data_vo import AssetMetadata
from .taxonomy_asset_request_vo import (
    AssetDownloadRequestVO,
    AssetDownloadResponseVO,
    AssetSearchRequestVO,
    AssetSearchResponseVO,
)


class AssetProviderPort(ABC):
    """Port interface for asset provider services."""

    @abstractmethod
    async def search_assets(
        self, request: AssetSearchRequestVO
    ) -> AssetSearchResponseVO:
        """Search for assets matching the query. Returns paginated results."""
        pass

    @abstractmethod
    async def get_asset_details(
        self, asset_id: AssetId
    ) -> AssetMetadata | None:
        """Get detailed metadata for a specific asset."""
        pass

    @abstractmethod
    async def download_asset(
        self, request: AssetDownloadRequestVO
    ) -> AssetDownloadResponseVO:
        """Download an asset to the specified destination. Returns download result."""
        pass
