"""Agent: Asset feature orchestrator.

Coordinates multi-provider asset search, download, and import.
"""

import logging

from modules.shared.src.asset import AssetMetadata, AssetSearchProtocol, ImportedAsset
from modules.shared.src.common.taxonomy_core_vo import AssetId, ProviderName, SearchQuery, StringList

logger = logging.getLogger("BlenderMCPServer")


class AssetOrchestrator:
    """Orchestrates asset search and import across providers."""

    def __init__(self, collector: AssetSearchProtocol):
        self._collector = collector

    async def search(self, query: SearchQuery, providers: StringList | None = None) -> list[AssetMetadata]:
        """Search assets across all registered providers."""
        return await self._collector.search_all(query, providers)

    async def fetch_and_import(self, provider_name: ProviderName, asset_id: AssetId) -> ImportedAsset:
        """Download from provider and import into Blender."""
        return await self._collector.fetch_and_import(provider_name, asset_id)
