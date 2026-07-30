from __future__ import annotations

import logging
from typing import cast

from modules.shared.src.asset.taxonomy_asset_vo import (
    AssetDownloadVO,
    AssetMetadataItem,
    AssetSearchVO,
)
from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    AssetCount,
    AssetId,
    AssetName,
    AssetType,
    ErrorMessage,
    FilePath,
    ProviderName,
    SearchQuery,
    SuccessFlag,
    TagList,
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

logger = logging.getLogger("BlenderMCPServer")

PROVIDER = ProviderName("Polyhaven")


async def polyhaven_search(
    connection: object,
    query: SearchQuery,
    categories: list[str] | None = None,
) -> AssetSearchVO:
    try:
        result = await connection.send_command(
            ActionName("search_polyhaven_assets"),
            {"asset_type": "all", "categories": categories or []},
        )
        items = [
            AssetMetadataItem(
                id=AssetId(asset_id),
                name=AssetName(data.get("name", asset_id)),
                type=AssetType(str(data.get("type", "unknown"))),
                provider=PROVIDER,
                tags=cast(TagList, data.get("categories", [])),
            )
            for asset_id, data in result.get("assets", {}).items()
        ]
        return AssetSearchVO(
            query=query,
            assets=items,
            total=AssetCount(len(items)),
            next_token=None,
            provider=PROVIDER,
        )
    except Exception as e:
        logger.error("Polyhaven search error: %s", e)
        raise ProviderError(str(e)) from e


async def polyhaven_get_details(connection: object, asset_id: str) -> dict[str, object] | None:
    try:
        result = await connection.send_command(
            ActionName("get_polyhaven_asset_details"), {"asset_id": asset_id}
        )
        if isinstance(result, dict) and "error" in result:
            logger.warning("Polyhaven get_asset_details error: %s", result["error"])
            return None
        return result
    except Exception as e:
        logger.error("Polyhaven details error: %s", e)
        return None


async def polyhaven_download(connection: object, request: AssetDownloadVO) -> AssetDownloadVO:
    try:
        result = await connection.send_command(
            ActionName("download_polyhaven_asset"),
            {"asset_id": str(request.asset_id), "asset_type": "models"},
        )
        if not result.get("success"):
            raise ProviderError(result.get("message", "Download failed"))
        return AssetDownloadVO(
            asset_id=request.asset_id,
            destination_path=request.destination_path,
            success=SuccessFlag(True),
            file_path=FilePath(str(result.get("path", ""))),
            message=ErrorMessage("Download successful"),
        )
    except Exception as e:
        logger.error("Polyhaven download error: %s", e)
        raise ProviderError(str(e)) from e
