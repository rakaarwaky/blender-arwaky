"""Asset taxonomy: ProviderMetadataVO value object."""

from __future__ import annotations

from dataclasses import dataclass, field

from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetName,
    AssetType,
    ProviderName,
    TagList,
    ThumbnailUrl,
)


@dataclass(frozen=True)
class ProviderMetadataVO:
    """Normalized provider metadata for an asset.

    FR-AST-005: Contains all standard metadata fields produced by
    AssetProviderMetadataCapability.normalize_metadata.
    """

    name: AssetName
    provider: ProviderName
    id: AssetId
    type: AssetType
    categories: TagList
    thumbnail_url: ThumbnailUrl | None = None
    license_summary: str | None = None
    download_available: bool = True
    attribution: str | None = None
    extra_fields: dict[str, object] = field(default_factory=dict)
    normalized_at: str = ""
