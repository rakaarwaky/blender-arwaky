"""Asset feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/asset/)    → VOs for search, download, extract, import
  - Contract (shared/src/asset/)   → AssetSearchProtocol, AssetDownloadProtocol,
                                      AssetExtractProtocol, AssetImportProtocol,
                                      AssetProviderMetadataProtocol
  - Capabilities                   → SearchCapability, DownloadCapability,
                                      ExtractCapability, ImportCapability,
                                      ProviderMetadataCapability
  - Agent                          → AssetOrchestrator
  - Root                           → AssetContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_asset_container
from .root_asset_container import AssetContainer, create_asset_container

__all__ = [
    "AssetContainer",
    "create_asset_container",
    "root_asset_container",
]
