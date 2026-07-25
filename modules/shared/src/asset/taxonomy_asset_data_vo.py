"""Asset metadata and imported asset value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from modules.shared.src.common.taxonomy_core_vo import ProviderName
from modules.shared.src.common.taxonomy_core_vo import AssetId, AssetName, AssetType, ObjectName, TagList, ThumbnailUrl


@dataclass(frozen=True)
class AssetMetadata:
    """Immutable metadata for an asset from a provider."""

    id: AssetId
    name: AssetName
    type: AssetType
    provider: ProviderName
    thumbnail_url: ThumbnailUrl | None = None
    tags: TagList = field(default_factory=lambda: cast(TagList, []))


@dataclass(frozen=True)
class ImportedAsset:
    """Result of importing an asset into Blender."""

    id: AssetId
    name: ObjectName
    blender_id: ObjectName


def create_asset_id(raw: str) -> AssetId:
    """Factory helper to create an AssetId from a raw string."""
    return AssetId(raw)


def create_provider_name(raw: str) -> ProviderName:
    """Factory helper to create a ProviderName from a raw string."""
    return ProviderName(raw)
