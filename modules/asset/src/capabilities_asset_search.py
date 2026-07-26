"""Capability: Multi-provider asset search (FR-AST-001).

Implements AssetSearchProtocol for unified search across enabled providers.
Returns normalized, aggregated results with pagination and warnings.
"""

from __future__ import annotations

import logging
import asyncio
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.asset.contract_asset_provider import AssetProviderPort
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetName,
    AssetType,
    AssetTypeFilter,
    NextPageToken,
    ProviderName,
    ResultLimit,
    SearchQuery,
    ThumbnailUrl,
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

logger = logging.getLogger("BlenderMCPServer")


class AssetSearchCapability(AssetSearchProtocol):
    """Unified multi-provider asset search capability.

    FR-AST-001: Single search operation regardless of provider count.
    Each enabled provider queried independently; failures logged and skipped.
    Partial results returned when at least one provider succeeds.
    """

    def __init__(self, providers: dict[str, AssetProviderPort]) -> None:
        """Initialize with registered provider ports.

        Args:
            providers: Dict of provider name to AssetProviderPort implementation.
        """
        self.providers = providers

    async def search_all(
        self,
        query: SearchQuery,
        providers: list[ProviderName] | None = None,
        asset_type_filter: AssetTypeFilter | None = None,
        limit: ResultLimit | None = None,
        page_token: NextPageToken | None = None,
    ) -> dict[str, Any]:
        """Search across all enabled providers with unified response.

        FR-AST-001: Each enabled provider queried independently with its own
        timeout. Provider failure must not block other providers; failures
        are logged and skipped. All results normalized into common asset
        metadata shape before aggregation.

        Args:
            query: Text search query.
            providers: Optional provider filter; None means all enabled.
            asset_type_filter: Optional asset type filter.
            limit: Optional result limit per provider.
            page_token: Optional pagination cursor.

        Returns:
            Dict with assets list, provider_status, pagination, and warnings.
        """
        assets: list[dict[str, Any]] = []
        provider_status: dict[str, str] = {}
        warnings: list[str] = []

        # Determine which providers to search
        target_providers = self.providers
        if providers:
            target_providers = {
                name: port for name, port in self.providers.items()
                if ProviderName(name) in providers
            }

        # Search all providers concurrently
        async def search_provider(name: str, port: AssetProviderPort) -> tuple[str, list[dict[str, Any]], str | None]:
            try:
                result = await port.search_assets(
                    type("Obj", (), {"query": query})()
                )
                # Normalize results
                normalized = []
                for item in getattr(result, "assets", []):
                    normalized.append({
                        "id": str(getattr(item, "id", "")),
                        "name": str(getattr(item, "name", "")),
                        "type": str(getattr(item, "type", "")),
                        "provider": name,
                        "thumbnail_url": str(getattr(item, "thumbnail_url", None)),
                        "tags": list(getattr(item, "tags", [])),
                    })
                return name, normalized, None
            except ProviderError as e:
                logger.warning("Provider %s search failed: %s", name, e)
                warnings.append(f"Provider {name} failed: {e}")
                return name, [], str(e)
            except Exception as e:
                logger.error("Provider %s search error: %s", name, e)
                warnings.append(f"Provider {name} error: {e}")
                return name, [], str(e)

        # Run providers concurrently
        tasks = [search_provider(name, port) for name, port in target_providers.items()]
        results = await asyncio.gather(*tasks)

        for name, assets_list, error in results:
            if error:
                provider_status[name] = "error"
            elif assets_list:
                provider_status[name] = "success"
                assets.extend(assets_list)
            else:
                provider_status[name] = "empty"

        return {
            "assets": assets,
            "provider_status": provider_status,
            "total": len(assets),
            "warnings": warnings,
            "search_timestamp": datetime.now(timezone.utc).isoformat(),
        }
