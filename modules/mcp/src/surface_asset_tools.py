"""MCP surface for real Asset aggregate search and download workflows."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable

from modules.shared.src.asset.contract_asset_aggregate import IAssetAggregate
from modules.shared.src.asset.taxonomy_asset_vo import AssetDownloadCacheVO
from modules.shared.src.common.taxonomy_core_vo import RequestId, SearchQuery, StringList, ToolName
from modules.shared.src.mcp.contract_mcp_protocol import McpResponseProtocol

logger = logging.getLogger("BlenderMCPServer")


class AssetToolsSurface:
    """MCP surface for Asset aggregate search and download."""

    @staticmethod
    def register_asset_tools(
        mcp,
        aggregate_factory: Callable[[], IAssetAggregate | None] | None = None,
        response_formatter: McpResponseProtocol | None = None,
    ):
        """Register Asset tools with explicit aggregate and response dependencies."""
        aggregate: IAssetAggregate | None = aggregate_factory() if aggregate_factory is not None else None
        if aggregate is None:
            return

        async def format_tool_result(tool_name: str, result: object, error_category: str | None = None) -> str:
            if response_formatter is None:
                return json.dumps(result, default=str)
            envelope = await response_formatter.format_response(
                result,
                ToolName(tool_name),
                RequestId(""),
                error_category=error_category,
            )
            return json.dumps(envelope, default=str)

        @mcp.tool()
        async def search_assets(query: str, providers_json: str = "[]") -> str:
            """Search for 3D assets across configured providers."""
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
                return await format_tool_result(
                    "search_assets",
                    {
                        "assets": [
                            {
                                "id": a.id,
                                "name": a.name,
                                "type": a.type,
                                "provider": a.provider,
                                "thumbnail_url": a.thumbnail_url,
                            }
                            for a in results
                        ],
                        "total": len(results),
                    },
                )
            except Exception as exc:
                logger.error("search_assets failed: %s", exc, exc_info=True)
                return await format_tool_result("search_assets", {"error": str(exc)}, "execution")

        @mcp.tool()
        async def download_asset(request_json: str) -> str:
            """Download an asset to the validated local cache directory."""
            try:
                request_data = json.loads(request_json) if request_json else {}
                vo = AssetDownloadCacheVO(**request_data)
                result = await aggregate.download_to_cache(vo)
                return await format_tool_result(
                    "download_asset",
                    {
                        "success": bool(result.success),
                        "file_path": result.file_path,
                        "file_size": result.file_size,
                        "cached": result.cached,
                        "integrity_ok": result.integrity_ok,
                        "message": result.message,
                    },
                )
            except Exception as exc:
                logger.error("download_asset failed: %s", exc, exc_info=True)
                return await format_tool_result("download_asset", {"error": str(exc)}, "execution")
