"""Capability: Sketchfab Asset Provider adapter.

Implements AssetProviderPort — fetches asset metadata and downloads from
the Sketchfab API through the server module's command dispatch capability.
"""

from __future__ import annotations

import logging
from typing import cast

from modules.gateway.src import IBlenderConnectionProtocol
from modules.shared.src.asset import (
    AssetMetadata,
    AssetMetadataVO,
    AssetProviderPort,
)
from modules.shared.src.asset.taxonomy_asset_vo import (
    AssetDownloadVO,
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
    SuccessFlag,
    TagList,
)
from modules.shared.src.common.taxonomy_domain_error import ProviderError

logger = logging.getLogger("BlenderMCPServer")


class SketchfabAssetAdapter(AssetProviderPort):
    """Implementation of AssetProviderPort for Sketchfab."""

    def __init__(self, connection: IBlenderConnectionProtocol) -> None:  # type: ignore[name-defined]
        """Initialize with a Blender connection from the server module.

        Args:
            connection: A Blender TCP connection for command dispatch.
        """
        self._connection = connection
        self.provider_name = "Sketchfab"

    async def search_assets(self, request: AssetSearchVO) -> AssetSearchVO:
        try:
            result = await self._connection.send_command(
                ActionName("search_sketchfab_models"),
                {"query": str(request.query), "count": 20, "downloadable": True},
            )

            assets: list[AssetMetadata] = []
            for model in result.get("results", []):
                assets.append(
                    AssetMetadata(
                        id=AssetId(model.get("uid", "")),
                        name=AssetName(model.get("name", "Unnamed model")),
                        type=AssetType("model"),
                        provider=ProviderName(self.provider_name),
                        tags=cast(TagList, []),
                    )
                )
            return AssetSearchVO(
                query=request.query,
                assets=[
                    AssetMetadataVO(
                        id=a.id,
                        name=a.name,
                        type=a.type,
                        provider=ProviderName(a.provider),
                        tags=a.tags,
                        thumbnail_url=None,
                    )
                    for a in assets
                ],
                total=AssetCount(len(assets)),
                next_token=None,
                provider=ProviderName(self.provider_name),
            )
        except Exception as e:
            logger.error("Sketchfab search error: %s", e)
            raise ProviderError(str(e)) from e

    async def get_asset_details(self, asset_id: str) -> AssetMetadata | None:
        """Get detailed info for a Sketchfab model."""
        try:
            result = await self._connection.send_command(
                ActionName("get_sketchfab_model_preview"), {"uid": asset_id}
            )
            if isinstance(result, dict) and "error" in result:
                logger.warning("Sketchfab get_asset_details error: %s", result["error"])
                return None
            return AssetMetadata(
                id=AssetId(asset_id),
                name=AssetName(result.get("model_name", asset_id)),
                type=AssetType("model"),
                provider=ProviderName(self.provider_name),
                tags=cast(TagList, []),
            )
        except Exception as e:
            logger.error("Sketchfab details error: %s", e)
            return None

    async def download_asset(self, request: AssetDownloadVO) -> AssetDownloadVO:
        try:
            target_size = 1.0
            result = await self._connection.send_command(
                ActionName("download_sketchfab_model"),
                {"uid": str(request.asset_id), "normalize_size": True, "target_size": target_size},
            )
            if not result.get("success"):
                raise ProviderError(result.get("message", "Download failed"))
            return AssetDownloadVO(
                asset_id=request.asset_id,
                destination_path=request.destination_path,
                success=SuccessFlag(True),
                file_path=FilePath(",".join(result.get("imported_objects", []))),
                message=ErrorMessage("Download successful"),  # type: ignore[arg-type]
            )
        except Exception as e:
            logger.error("Sketchfab download error: %s", e)
            raise ProviderError(str(e)) from e
