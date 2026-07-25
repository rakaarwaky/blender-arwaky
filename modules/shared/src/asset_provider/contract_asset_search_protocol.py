"""Asset provider domain contract: asset search protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import AssetId, ProviderName, SearchQuery, StringList
from .taxonomy_asset_data_vo import AssetMetadata, ImportedAsset


class ContractAssetSearchProtocol(ABC):
    """Business logic interface for asset searching and importing."""

    @abstractmethod
    async def search_all(
        self, query: SearchQuery, providers: StringList | None = None
    ) -> list[AssetMetadata]:
        """Search across all registered providers, optionally filtered."""
        pass

    @abstractmethod
    async def fetch_and_import(
        self, provider_name: ProviderName, asset_id: AssetId
    ) -> ImportedAsset:
        """Download from specific provider and import into Blender."""
        pass
