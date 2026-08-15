"""MCP Tool: Asset operations — search and download via IAssetAggregate.

FR-AST-001: Search Assets Across Providers — search tool registered with MCP server
FR-AST-002: Download Asset to Cache — download tool delegates to aggregate
FR-MCP-001: Expose MCP Tools — asset tools registered with MCP server
FR-MCP-002: Route Tool Calls — delegates to IAssetAggregate through aggregate factory
FR-MCP-003: Format MCP Responses — returns structured result from aggregate
"""

import json
import logging
from collections.abc import Callable

from modules.shared.src.asset.contract_asset_aggregate import IAssetAggregate
from modules.shared.src.asset.taxonomy_asset_vo import AssetDownloadCacheVO
from modules.shared.src.common.taxonomy_core_vo import SearchQuery, StringList

logger = logging.getLogger("BlenderMCPServer")


class AssetToolsSurface:
    """MCP surface for asset search and download tools."""

    @staticmethod
    def register_asset_tools(mcp, aggregate_factory: Callable[[], IAssetAggregate | None] | None = None):
        """Register asset search and download tools with MCP server.

        Args:
            mcp: MCP server instance
            aggregate_factory: Optional factory that returns IAssetAggregate.
        """
        aggregate: IAssetAggregate | None = None
        if aggregate_factory is not None:
            aggregate = aggregate_factory()

        if aggregate is None:
            return

        @mcp.tool()
        async def search_assets(query: str, providers_json: str = "[]") -> str:
            """Search for 3D assets across configured providers.

            Args:
                query: Search text (e.g. 'wooden table', 'sci-fi helmet')
                providers_json: JSON array of provider names to filter (default: all)

            Returns:
                JSON string with matching assets including id, name, type, provider, thumbnail.
            """
            try:
                provider_list: list[str] | None = None
                if providers_json:
                    parsed = json.loads(providers_json)
                    if isinstance(parsed, list) and parsed:
                        provider_list = parsed
                results = await aggregate.search(
                    query=SearchQuery(query),
                    providers=StringList(provider_list) if provider_list else None,
                )
                return json.dumps(
                    [
                        {
                            "id": a.id,
                            "name": a.name,
                            "type": a.type,
                            "provider": a.provider,
                            "thumbnail_url": a.thumbnail_url,
                        }
                        for a in results
                    ],
                    default=str,
                )
            except Exception as e:
                logger.error("search_assets failed: %s", e, exc_info=True)
                return json.dumps({"error": str(e), "success": False})

        @mcp.tool()
        async def download_asset(request_json: str) -> str:
            """Download an asset to the local cache directory.

            Args:
                request_json: JSON string with AssetDownloadCacheVO fields:
                    - provider: provider name (e.g. 'polyhaven')
                    - asset_id: asset identifier
                    - asset_type: type (e.g. 'texture', 'model', 'hdr')
                    - cache_dir: local cache directory path
                    - resolution: optional resolution preference
                    - overwrite_policy: 'reuse' or 'overwrite' (default: 'reuse')
                    - max_size: optional max download size in bytes

            Returns:
                JSON string with download result including file_path, cached status.
            """
            try:
                request_data = json.loads(request_json) if request_json else {}
                vo = AssetDownloadCacheVO(**request_data)
                result = await aggregate.download_to_cache(vo)
                return json.dumps(
                    {
                        "success": bool(result.success),
                        "file_path": result.file_path,
                        "file_size": result.file_size,
                        "cached": result.cached,
                        "integrity_ok": result.integrity_ok,
                        "message": result.message,
                    },
                    default=str,
                )
            except Exception as e:
                logger.error("download_asset failed: %s", e, exc_info=True)
                return json.dumps({"error": str(e), "success": False})
