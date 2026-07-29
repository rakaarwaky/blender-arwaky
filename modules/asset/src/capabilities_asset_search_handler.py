"""Capability: Asset search across providers.

FR-AST-001: Unified search across Polyhaven and Sketchfab providers.
Returns normalized, aggregated results with provider status summary.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.asset.utility.utility_polyhaven_search import polyhaven_search
from modules.shared.src.asset.utility.utility_sketchfab_search import sketchfab_search
from modules.shared.src.common.taxonomy_core_vo import SearchQuery

logger = logging.getLogger("BlenderMCPServer")


class AssetSearchHandler(AssetSearchProtocol):
    """Asset search handler with configurable provider list.

    FR-AST-001: Unified search across providers. Defaults to Polyhaven and Sketchfab.
    Providers can be overridden at call time or via constructor injection.
    """

    def __init__(self, connection: object, providers: list[str] | None = None) -> None:
        self._connection = connection
        self._providers = providers if providers is not None else ["Polyhaven", "Sketchfab"]

    async def search_all(
        self,
        query: SearchQuery,
        providers: list[str] | None = None,
        _asset_type_filter: Any = None,
        _limit: Any = None,
        _page_token: Any = None,
    ) -> dict[str, Any]:
        """Search across all enabled providers with unified response.

        FR-AST-001: Each enabled provider queried independently.
        Failures logged and skipped; partial results returned when possible.
        Results normalized into common asset metadata shape before aggregation.

        Args:
            query: Text search query.
            providers: Optional provider filter; None means use configured defaults.
            _asset_type_filter: Optional asset type filter (interface param).
            _limit: Optional result limit per provider (interface param).
            _page_token: Optional pagination cursor (interface param).

        Returns:
            Dict with normalized assets list, provider status summary, warnings, and timestamp.
        """
        target = providers if providers is not None else self._providers

        async def search_one(name: str) -> tuple[str, list[Any], str | None]:
            try:
                if name == "Polyhaven":
                    vo = await polyhaven_search(self._connection, query)
                elif name == "Sketchfab":
                    vo = await sketchfab_search(self._connection, query)
                else:
                    return name, [], "unknown provider"
                normalized = [
                    {
                        "id": str(a.id),
                        "name": str(a.name),
                        "type": str(a.type),
                        "provider": str(a.provider),
                        "thumbnail_url": str(a.thumbnail_url) if a.thumbnail_url else None,
                        "tags": list(a.tags),
                    }
                    for a in vo.assets
                ]
                return name, normalized, None
            except Exception as e:
                logger.warning("Provider %s search failed: %s", name, e)
                return name, [], str(e)

        tasks = [search_one(str(p)) for p in target]
        results = await asyncio.gather(*tasks)

        assets: list[Any] = []
        provider_status: dict[str, str] = {}
        warnings: list[str] = []

        for name, items, error in results:
            if error:
                provider_status[name] = "error"
                warnings.append(f"Provider {name} failed: {error}")
            elif items:
                provider_status[name] = "success"
                assets.extend(items)
            else:
                provider_status[name] = "empty"

        return {
            "assets": assets,
            "total": len(assets),
            "provider_status": provider_status,
            "warnings": warnings,
            "search_timestamp": datetime.now(timezone.utc).isoformat(),
        }
