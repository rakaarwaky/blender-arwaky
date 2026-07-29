"""Asset feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/asset/)    → VOs for search, download, extract, import
  - Contract (shared/src/asset/)   → AssetSearchProtocol, AssetDownloadProtocol,
                                      AssetExtractProtocol, AssetImportProtocol,
                                      AssetProviderProtocol
  - Capabilities                   → SearchCapability, DownloadCapability,
                                      ExtractCapability, ImportCapability,
                                      ProviderMetadataCapability
  - Agent                          → AssetOrchestrator
  - Root                           → AssetContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from .agent_asset_orchestrator import AssetOrchestrator
from .capabilities_asset_download import AssetDownloadCapability
from .capabilities_asset_extract import AssetExtractCapability
from .capabilities_asset_import import AssetImportCapability
from .capabilities_asset_provider import AssetProviderMetadataCapability
from .capabilities_asset_search_handler import AssetSearchHandler
from .root_asset_container import AssetContainer, create_asset_container

__all__ = [
    "AssetOrchestrator",
    "AssetDownloadCapability",
    "AssetExtractCapability",
    "AssetImportCapability",
    "AssetProviderMetadataCapability",
    "AssetSearchHandler",
    "AssetContainer",
    "create_asset_container",
]
