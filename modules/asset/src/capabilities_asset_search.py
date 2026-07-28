from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
from modules.shared.src.asset.utility.utility_polyhaven import polyhaven_search
from modules.shared.src.asset.utility.utility_sketchfab import sketchfab_search
from modules.shared.src.common.taxonomy_core_vo import (
    AssetTypeFilter,
    NextPageToken,
    ProviderName,
    ResultLimit,
    SearchQuery,
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

logger = logging.getLogger("BlenderMCPServer")

PROVIDER_NAMES = ["Polyhaven", "Sketchfab"]


class AssetSearchCapability(AssetSearchProtocol):
    def __init__(self, connection: object) -> None:
        self._connection = connection

    async def search_all(
        self,
        query: SearchQuery,
        providers: list[ProviderName] | None = None,
        asset_type_filter: AssetTypeFilter | None = None,
        limit: ResultLimit | None = None,
        page_token: NextPageToken | None = None,
    ) -> dict[str, Any]:
        target = providers if providers is not None else PROVIDER_NAMES

        async def search_one(name: str) -> tuple[str, list[dict[str, Any]], str | None]:
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
            except ProviderError as e:
                logger.warning("Provider %s search failed: %s", name, e)
                return name, [], str(e)
            except Exception as e:
                logger.error("Provider %s search error: %s", name, e)
                return name, [], str(e)

        tasks = [search_one(str(p)) for p in target]
        results = await asyncio.gather(*tasks)

        assets: list[dict[str, Any]] = []
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
            "provider_status": provider_status,
            "total": len(assets),
            "warnings": warnings,
            "search_timestamp": datetime.now(timezone.utc).isoformat(),
        }
