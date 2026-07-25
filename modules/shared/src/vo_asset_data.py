"""Asset metadata and imported asset value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, cast

from .constant_asset_types import ProviderName
from .constant_core_types import AssetId, AssetName, AssetType, ObjectName, TagList, ThumbnailUrl


@dataclass(frozen=True)
class AssetMetadata:
    """Immutable metadata for an asset from a provider."""

    id: AssetId
    name: AssetName
    type: AssetType  # "hdris", "textures", "model"
    provider: ProviderName
    thumbnail_url: ThumbnailUrl | None = None
    tags: TagList = field(default_factory=lambda: cast(TagList, []))


@dataclass(frozen=True)
class ImportedAsset:
    """Result of importing an asset into Blender."""

    id: AssetId
    name: ObjectName
    blender_id: ObjectName  # Blender internal object name


def create_asset_id(raw: str) -> AssetId:
    """Factory helper to create an AssetId from a raw string."""
    return AssetId(raw)
