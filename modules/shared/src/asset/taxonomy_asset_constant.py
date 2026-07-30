"""Asset type and provider name constants."""

from __future__ import annotations

from typing import Final

from modules.shared.src.common.taxonomy_core_vo import AssetType, ProviderName

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

# ============================================================
# IMPORT & EXPORT DEFAULT CONSTANTS
# ============================================================

DEFAULT_MERGE_OBJECTS: Final[bool] = True
DEFAULT_APPLY_MODIFIERS: Final[bool] = False
DEFAULT_INCLUDE_TYPES: Final[tuple[str, ...]] = ("MESH", "CAMERA", "LIGHT", "EMPTY")

DEFAULT_SELECTED_ONLY: Final[bool] = False
DEFAULT_CODEC: Final[str] = "ZIP"
DEFAULT_MAX_TREE_DEPTH: Final[int] = 1024

DEFAULT_OVERWRITE_POLICY: Final[str] = "reuse"
DEFAULT_DUPLICATE_POLICY: Final[str] = "rename"

# Supported file formats
SUPPORTED_IMPORT_FORMATS: Final[tuple[str, ...]] = (
    "GLB",
    "GLTF",
    "OBJ",
    "STL",
    "FBX",
    "DAE",
    "PNG",
    "JPG",
    "JPEG",
    "EXR",
    "TGA",
    "HDR",
)

SUPPORTED_EXPORT_FORMATS: Final[tuple[str, ...]] = (
    "GLTF",
    "GLB",
    "OBJ",
    "STL",
)

