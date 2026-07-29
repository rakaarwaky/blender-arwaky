"""Surface: Asset search command handler.

FR-AST-001: Exposes asset search through the MCP surface layer.
Depends on IAssetAggregate contract — no direct capability imports.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.asset.contract_asset_aggregate import IAssetAggregate
from modules.shared.src.common.taxonomy_core_vo import SearchQuery, StringList

logger = logging.getLogger("BlenderMCPServer")


class AssetSearchSurface:
    """Surface handler for asset search operations.

    Delegates all business logic to IAssetAggregate orchestrator.
    This is the entry point for the MCP surface layer to call into
    the asset feature — fulfilling the AES 505 requirement that
    agent orchestrators must have a surface consumer.
    """

    def __init__(self, aggregate: IAssetAggregate) -> None:
        self._aggregate = aggregate

    async def search_assets(
        self,
        query_text: str,
        providers: StringList | None = None,
    ) -> list[dict[str, Any]]:
        """Search assets across configured providers.

        Args:
            query_text: Text search query.
            providers: Optional provider filter; None means use defaults.

        Returns:
            List of asset metadata dicts from the orchestrator.
        """
        query = SearchQuery(query_text)
        assets = await self._aggregate.search(query, providers)
        return [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "provider": a.provider,
            }
            for a in assets
        ]
