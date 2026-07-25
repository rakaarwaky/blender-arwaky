"""Asset domain — taxonomy types and contracts."""

from .taxonomy_asset_constant import (
    ASSET_TYPE_HDRIS,
    ASSET_TYPE_MODELS,
    ASSET_TYPE_TEXTURES,
    PROVIDER_POLYHAVEN,
    PROVIDER_SKETCHFAB,
)

from .taxonomy_asset_data_vo import (
    AssetMetadata,
    ImportedAsset,
    create_asset_id,
    create_provider_name,
)

from .taxonomy_asset_request_vo import (
    AssetDownloadRequestVO,
    AssetDownloadResponseVO,
    AssetMetadataItem,
    AssetMetadataVO,
    AssetSearchRequestVO,
    AssetSearchResponseVO,
)

from .taxonomy_import_export_vo import (
    ExportModelRequestVO,
    ExportModelResponseVO,
    ImportGlbRequestVO,
    ImportGlbResponseVO,
)

from .asset_provider_port import AssetProviderPort
from .asset_search_protocol import AssetSearchProtocol
from .import_export_protocol import ImportExportProtocol
from .polyhaven_api_port import PolyhavenApiPort
from .sketchfab_api_port import SketchfabApiPort

__all__ = [
    # Constants
    "ASSET_TYPE_HDRIS",
    "ASSET_TYPE_MODELS",
    "ASSET_TYPE_TEXTURES",
    "PROVIDER_POLYHAVEN",
    "PROVIDER_SKETCHFAB",
    # VOs
    "AssetMetadata",
    "AssetMetadataItem",
    "AssetMetadataVO",
    "ImportedAsset",
    "AssetSearchRequestVO",
    "AssetSearchResponseVO",
    "AssetDownloadRequestVO",
    "AssetDownloadResponseVO",
    "ImportGlbRequestVO",
    "ImportGlbResponseVO",
    "ExportModelRequestVO",
    "ExportModelResponseVO",
    # Factories
    "create_asset_id",
    "create_provider_name",
    # Contracts — Ports
    "AssetProviderPort",
    "PolyhavenApiPort",
    "SketchfabApiPort",
    # Contracts — Protocols
    "AssetSearchProtocol",
    "ImportExportProtocol",
]
