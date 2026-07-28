from __future__ import annotations

import logging

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
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

logger = logging.getLogger("BlenderMCPServer")

PROVIDER = ProviderName("Sketchfab")


async def sketchfab_search(
    connection: object,
    query: SearchQuery,
) -> AssetSearchVO:
    try:
        result = await connection.send_command(
            ActionName("search_sketchfab_models"),
            {"query": str(query), "count": 20, "downloadable": True},
        )
        items = [
            AssetMetadataItem(
                id=AssetId(model.get("uid", "")),
                name=AssetName(model.get("name", "Unnamed model")),
                type=AssetType("model"),
                provider=PROVIDER,
            )
            for model in result.get("results", [])
        ]
        return AssetSearchVO(
            query=query,
            assets=items,
            total=AssetCount(len(items)),
            next_token=None,
            provider=PROVIDER,
        )
    except Exception as e:
        logger.error("Sketchfab search error: %s", e)
        raise ProviderError(str(e)) from e


async def sketchfab_get_details(connection: object, asset_id: str) -> dict | None:
    try:
        result = await connection.send_command(
            ActionName("get_sketchfab_model_preview"), {"uid": asset_id}
        )
        if isinstance(result, dict) and "error" in result:
            logger.warning("Sketchfab get_asset_details error: %s", result["error"])
            return None
        return result
    except Exception as e:
        logger.error("Sketchfab details error: %s", e)
        return None


async def sketchfab_download(connection: object, request: AssetDownloadVO) -> AssetDownloadVO:
    try:
        result = await connection.send_command(
            ActionName("download_sketchfab_model"),
            {"uid": str(request.asset_id), "normalize_size": True, "target_size": 1.0},
        )
        if not result.get("success"):
            raise ProviderError(result.get("message", "Download failed"))
        return AssetDownloadVO(
            asset_id=request.asset_id,
            destination_path=request.destination_path,
            success=SuccessFlag(True),
            file_path=FilePath(",".join(result.get("imported_objects", []))),
            message=ErrorMessage("Download successful"),
        )
    except Exception as e:
        logger.error("Sketchfab download error: %s", e)
        raise ProviderError(str(e)) from e
