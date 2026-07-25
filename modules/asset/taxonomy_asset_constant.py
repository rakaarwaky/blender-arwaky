"""Asset type and provider name constants."""

from __future__ import annotations

from typing import Final

from ..common.taxonomy_core_vo import AssetType, ProviderName

# ============================================================
# ASSET TYPE CONSTANTS
# ============================================================

ASSET_TYPE_HDRIS: Final[AssetType] = AssetType("hdris")
ASSET_TYPE_TEXTURES: Final[AssetType] = AssetType("textures")
ASSET_TYPE_MODELS: Final[AssetType] = AssetType("models")

# ============================================================
# PROVIDER CONSTANTS
# ============================================================

PROVIDER_POLYHAVEN: Final[ProviderName] = ProviderName("tool_search_polyhaven")
PROVIDER_SKETCHFAB: Final[ProviderName] = ProviderName("tool_search_sketchfab")
