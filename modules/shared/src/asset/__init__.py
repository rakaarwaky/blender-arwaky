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

from .taxonomy_asset_vo import (
    AssetDownloadVO,
    AssetExtractArchiveVO,
    AssetImportBlenderVO,
    AssetMetadataItem,
    AssetMetadataVO,
    AssetDownloadCacheVO,
    ExportModelVO,
    ImportGlbVO,
)

from .contract_asset_provider import AssetProviderPort
from .contract_asset_search_protocol import AssetSearchProtocol
from .contract_asset_download_protocol import AssetDownloadProtocol
from .contract_asset_extract_protocol import AssetExtractProtocol
from .contract_asset_import_protocol import AssetImportProtocol
from .contract_import_export_protocol import ImportExportProtocol
from .contract_library_download_protocol import LibraryDownloadProtocol, LibraryDownloadResult
from .contract_library_search_protocol import LibraryAssetMetadata, LibrarySearchProtocol, LibrarySearchResponse
from .contract_marketplace_download_protocol import MarketplaceDownloadProtocol, MarketplaceDownloadResult
from .contract_marketplace_search_protocol import MarketplaceSearchProtocol
from .contract_polyhaven_api import PolyhavenApiPort
from .contract_sketchfab_api import SketchfabApiPort

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
    "AssetSearchVO",
    "AssetDownloadVO",
    "AssetDownloadCacheVO",
    "AssetExtractArchiveVO",
    "AssetImportBlenderVO",
    "ImportGlbVO",
    "ExportModelVO",
    # Library/Marketplace VOs
    "LibraryAssetMetadata",
    "LibrarySearchResponse",
    "LibraryDownloadResult",
    "MarketplaceDownloadResult",
    # Factories
    "create_asset_id",
    "create_provider_name",
    # Contracts — Ports
    "AssetProviderPort",
    "PolyhavenApiPort",
    "SketchfabApiPort",
    # Contracts — Protocols
    "AssetSearchProtocol",
    "AssetDownloadProtocol",
    "AssetExtractProtocol",
    "AssetImportProtocol",
    "ImportExportProtocol",
    "LibrarySearchProtocol",
    "LibraryDownloadProtocol",
    "MarketplaceSearchProtocol",
    "MarketplaceDownloadProtocol",
]
