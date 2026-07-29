from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.asset.taxonomy_asset_data_vo import AssetMetadata
from modules.shared.src.asset.taxonomy_asset_vo import (
    AssetDownloadCacheVO,
    AssetExtractArchiveVO,
    AssetImportBlenderVO,
)
from modules.shared.src.common.taxonomy_core_vo import AssetId, ProviderName, SearchQuery, StringList


class IAssetAggregate(ABC):
    """Aggregate facade for asset operations.

    Implemented by Agent layer (AssetOrchestrator). Surface layer depends on it.
    """

    @abstractmethod
    async def search(self, query: SearchQuery, providers: StringList | None = None) -> list[AssetMetadata]:
        ...

    @abstractmethod
    async def download_to_cache(self, request: AssetDownloadCacheVO) -> AssetDownloadCacheVO:
        ...

    @abstractmethod
    async def extract_archive(self, request: AssetExtractArchiveVO) -> AssetExtractArchiveVO:
        ...

    @abstractmethod
    async def import_asset(self, request: AssetImportBlenderVO) -> AssetImportBlenderVO:
        ...

    @abstractmethod
    async def get_provider_metadata(self, provider_name: ProviderName, asset_id: AssetId) -> dict[str, Any]:
        ...
