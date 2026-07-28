"""Aggregate contract for the asset feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_asset_download_protocol import AssetDownloadProtocol
from .contract_asset_extract_protocol import AssetExtractProtocol
from .contract_asset_import_protocol import AssetImportProtocol
from .contract_asset_provider import AssetProviderPort
from .contract_asset_provider_metadata_protocol import AssetProviderMetadataProtocol
from .contract_asset_search_protocol import AssetSearchProtocol
from .contract_import_export_protocol import ImportExportProtocol
from .contract_library_download_protocol import LibraryDownloadProtocol
from .contract_library_search_protocol import LibrarySearchProtocol
from .contract_marketplace_download_protocol import MarketplaceDownloadProtocol
from .contract_marketplace_search_protocol import MarketplaceSearchProtocol
from .contract_polyhaven_api import PolyhavenApiPort
from .contract_sketchfab_api import SketchfabApiPort

__all__ = [
    "AssetDownloadProtocol",
    "AssetExtractProtocol",
    "AssetImportProtocol",
    "AssetProviderPort",
    "AssetProviderMetadataProtocol",
    "AssetSearchProtocol",
    "ImportExportProtocol",
    "LibraryDownloadProtocol",
    "LibrarySearchProtocol",
    "MarketplaceDownloadProtocol",
    "MarketplaceSearchProtocol",
    "PolyhavenApiPort",
    "SketchfabApiPort",
]
