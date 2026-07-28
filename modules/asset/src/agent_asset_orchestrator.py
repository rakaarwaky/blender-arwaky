"""Agent: Asset feature orchestrator.

Implements IAssetAggregate — single entry point for Surface layer
across search, download, extract, import, and provider metadata.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from modules.shared.src.asset.contract_asset_aggregate import IAssetAggregate
from modules.shared.src.asset.contract_asset_download_protocol import AssetDownloadProtocol
from modules.shared.src.asset.contract_asset_extract_protocol import AssetExtractProtocol
from modules.shared.src.asset.contract_asset_import_protocol import AssetImportProtocol
from modules.shared.src.asset.contract_asset_provider_protocol import AssetProviderProtocol
from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.asset.taxonomy_asset_data_vo import AssetMetadata, ImportedAsset
from modules.shared.src.asset.taxonomy_asset_vo import (
    AssetDownloadCacheVO,
    AssetExtractArchiveVO,
    AssetImportBlenderVO,
)
from modules.shared.src.common.taxonomy_core_vo import AssetId, ProviderName, SearchQuery, StringList

logger = logging.getLogger("BlenderMCPServer")


class AssetOrchestrator(IAssetAggregate):
    def __init__(
        self,
        search_capability: AssetSearchProtocol,
        download_capability: AssetDownloadProtocol | None = None,
        extract_capability: AssetExtractProtocol | None = None,
        import_capability: AssetImportProtocol | None = None,
        metadata_capability: AssetProviderProtocol | None = None,
    ) -> None:
        self._search = search_capability
        self._download = download_capability
        self._extract = extract_capability
        self._import = import_capability
        self._metadata = metadata_capability

    async def search(self, query: SearchQuery, providers: StringList | None = None) -> list[AssetMetadata]:
        result = await self._search.search_all(query, providers)
        assets: list[dict[str, Any]] = result.get("assets", [])
        return [
            AssetMetadata(
                id=cast(str, a.get("id", "")),
                name=cast(str, a.get("name", "")),
                type=cast(str, a.get("type", "")),
                provider=cast(str, a.get("provider", "")),
            )
            for a in assets
        ]

    async def download_to_cache(self, request: AssetDownloadCacheVO) -> AssetDownloadCacheVO:
        if self._download is None:
            raise NotImplementedError("Download capability not configured")
        raw = await self._download.download_to_cache(
            provider=request.provider,
            asset_id=request.asset_id,
            asset_type=request.asset_type,
            cache_dir=request.cache_dir,
            resolution=request.resolution,
            overwrite_policy=request.overwrite_policy,
            max_size=request.max_size,
            background=False,
        )
        return AssetDownloadCacheVO(
            provider=request.provider,
            asset_id=request.asset_id,
            asset_type=request.asset_type,
            cache_dir=request.cache_dir,
            resolution=request.resolution,
            overwrite_policy=request.overwrite_policy,
            max_size=request.max_size,
            success=raw.get("success", False),
            file_path=raw.get("file_path", None),
            file_size=raw.get("file_size", 0),
            cached=raw.get("cached", False),
            integrity_ok=raw.get("integrity_ok", True),
            message=raw.get("message", ""),
        )

    async def extract_archive(self, request: AssetExtractArchiveVO) -> AssetExtractArchiveVO:
        if self._extract is None:
            raise NotImplementedError("Extract capability not configured")
        raw = await self._extract.extract_archive(
            artifact_path=request.artifact_path,
            destination=request.destination,
            max_entries=request.max_entries,
            max_extracted_size=request.max_extracted_size,
            allow_symlinks=request.allow_symlinks,
        )
        return AssetExtractArchiveVO(
            artifact_path=request.artifact_path,
            destination=request.destination,
            max_entries=request.max_entries,
            max_extracted_size=request.max_extracted_size,
            allow_symlinks=request.allow_symlinks,
            success=raw.get("success", False),
            extracted_files=raw.get("extracted_files", ()),
            rejected_entries=raw.get("rejected_entries", ()),
            message=raw.get("message", ""),
        )

    async def import_asset(self, request: AssetImportBlenderVO) -> AssetImportBlenderVO:
        if self._import is None:
            raise NotImplementedError("Import capability not configured")
        raw = await self._import.import_asset(
            file_path=request.file_path,
            asset_type=request.asset_type,
            target_collection=request.target_collection,
            scale_normalization=request.scale_normalization,
            duplicate_policy=request.duplicate_policy,
            format_hint=request.format_hint,
        )
        return AssetImportBlenderVO(
            file_path=request.file_path,
            asset_type=request.asset_type,
            target_collection=request.target_collection,
            scale_normalization=request.scale_normalization,
            duplicate_policy=request.duplicate_policy,
            format_hint=request.format_hint,
            success=raw.get("success", False),
            object_names=raw.get("object_names", ()),
            asset_name=raw.get("asset_name", ""),
            license_summary=raw.get("license_summary", ""),
            message=raw.get("message", ""),
        )

    async def get_provider_metadata(self, provider_name: ProviderName, asset_id: AssetId) -> dict[str, Any]:
        if self._metadata is None:
            raise NotImplementedError("Provider metadata capability not configured")
        return await self._metadata.normalize_metadata({}, provider_name, asset_id)
