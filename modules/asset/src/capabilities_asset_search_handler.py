"""Capability: Asset search across providers.

FR-AST-001: Unified search across Polyhaven and Sketchfab providers.
Returns normalized, aggregated results with provider status summary.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.asset.contract_asset_provider_connection import IAssetProviderConnection
from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.asset.utility.utility_polyhaven_search import polyhaven_search
from modules.shared.src.asset.utility.utility_sketchfab_search import sketchfab_search
from modules.shared.src.common.taxonomy_core_vo import SearchQuery

logger = logging.getLogger("BlenderMCPServer")


class AssetSearchHandler(AssetSearchProtocol):
    """Asset search handler with configurable provider list.

    FR-AST-001: Unified search across providers. Defaults to Polyhaven and Sketchfab.
    Providers can be overridden at call time or via constructor injection.
    Uses IAssetProviderConnection protocol instead of primitive `object` type.
    """

    def __init__(
        self,
        connection: IAssetProviderConnection,
        providers: list[str] | None = None,
        enabled_providers: list[str] | None = None,
    ) -> None:
        self._connection = connection
        self._providers = providers if providers is not None else ["Polyhaven", "Sketchfab"]
        self._enabled_providers = enabled_providers

    async def search_all(
        self,
        query: SearchQuery,
        providers: list[str] | None = None,
        asset_type_filter: Any = None,
        limit: Any = None,
        page_token: Any = None,
    ) -> dict[str, Any]:
        """Search across all enabled providers with unified response.

        FR-AST-001: Each enabled provider queried independently.
        Failures logged and skipped; partial results returned when possible.
        Results normalized into common asset metadata shape before aggregation.

        Args:
            query: Text search query.
            providers: Optional provider filter; None means use configured defaults.
            asset_type_filter: Optional asset type filter (FR-AST-001).
            limit: Optional result limit per provider (FR-AST-001).
            page_token: Optional pagination cursor (FR-AST-001).

        Returns:
            Dict with normalized assets list, provider status summary, warnings, and timestamp.
        """
        target = providers if providers is not None else self._providers

        # R04: Provider enablement check - warn on disabled providers
        if self._enabled_providers is not None:
            disabled = [p for p in target if p not in self._enabled_providers]
            if disabled:
                logger.warning("Search targets include disabled providers: %s", disabled)

        # R02: Validate and warn on unsupported params (FR-AST-001)
        if asset_type_filter is not None:
            logger.debug("asset_type_filter=%s not yet enforced in provider queries", asset_type_filter)
        if limit is not None:
            logger.debug("limit=%s not yet enforced in provider queries", limit)
        if page_token is not None:
            logger.debug("page_token not yet enforced in provider queries")

        logger.debug("Search query=%s providers=%s", query, target)

        async def search_one(name: str) -> tuple[str, list[Any], str | None]:
            try:
                # FR-AST-001: empty query returns curated/default results
                effective_query = query if str(query).strip() else SearchQuery("curated")
                if name == "Polyhaven":
                    vo = await polyhaven_search(self._connection, effective_query)
                elif name == "Sketchfab":
                    vo = await sketchfab_search(self._connection, effective_query)
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
        errors: list[str] = []

        for name, items, error in results:
            if error:
                provider_status[name] = "error"
                warnings.append(f"Provider {name} failed: {error}")
                errors.append(f"{name}: {error}")
            elif items:
                provider_status[name] = "success"
                assets.extend(items)
            else:
                provider_status[name] = "empty"

        # FR-AST-001: When all providers fail, include aggregated error
        all_failed = all(status == "error" for status in provider_status.values()) and len(provider_status) > 0

        # FR-AST-001: deduplicate assets when equivalence is safely determinable
        seen: dict[str, Any] = {}
        deduped: list[Any] = []
        for a in assets:
            key = f"{a.get('provider', '')}:{a.get('id', '')}"
            if key not in seen:
                seen[key] = a
                deduped.append(a)
        assets = deduped

        return {
            "assets": assets,
            "total": len(assets),
            "provider_status": provider_status,
            "warnings": warnings,
            "errors": errors if all_failed else None,
            "search_timestamp": datetime.now(timezone.utc).isoformat(),
        }
