"""Asset search and download request/response value objects."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    AssetId,
    AssetName,
    AssetType,
    FilePath,
    ObjectName,
    ProviderName,
    SearchQuery,
    TagList,
    ThumbnailUrl,
)


@dataclass(frozen=True)
class AssetSearchRequestVO:
    """Request to search for assets."""

    query: SearchQuery


@dataclass(frozen=True)
class AssetMetadataItem:
    """Individual asset metadata item from search results."""

    id: AssetId
    name: AssetName
    type: AssetType
    provider: ProviderName
    thumbnail_url: ThumbnailUrl | None = None
    tags: TagList = field(default_factory=lambda: TagList([]))


@dataclass(frozen=True)
class AssetSearchResponseVO:
    """Response from an asset search operation."""

    assets: list[AssetMetadataItem]


@dataclass(frozen=True)
class AssetDownloadRequestVO:
    """Request to download an asset."""

    asset_id: AssetId
    destination_path: FilePath


@dataclass(frozen=True)
class AssetDownloadResponseVO:
    """Response from an asset download operation."""

    file_path: FilePath | None
