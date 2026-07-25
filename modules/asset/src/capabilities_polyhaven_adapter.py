"""Capability: Polyhaven Asset Provider adapter.

Implements AssetProviderPort — fetches asset metadata and downloads from
the Polyhaven API through the server module's command dispatch capability.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from modules.shared.src.asset import (
    AssetDownloadRequestVO,
    AssetDownloadResponseVO,
    AssetProviderPort,
    AssetSearchRequestVO,
    AssetSearchResponseVO,
)
from modules.shared.src.asset import (
    AssetMetadata,
    AssetMetadataVO,
)
from modules.shared.src.common.taxonomy_core_vo import (
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

if TYPE_CHECKING:
    from modules.shared.src.server.contract_command_protocol import IBlenderCommandProtocol

logger = logging.getLogger("BlenderMCPServer")


class PolyhavenAssetAdapter(AssetProviderPort):
    """Implementation of AssetProviderPort for Polyhaven."""

    def __init__(self, command_sender: IBlenderCommandProtocol) -> None:  # type: ignore[name-defined]
        """Initialize with a command sender from the server module.

        Args:
            command_sender: A callable that sends commands to Blender.
        """
        self._command_sender = command_sender
        self.provider_name = "Polyhaven"

    async def search_assets(self, request: AssetSearchRequestVO) -> AssetSearchResponseVO:
        try:
            result = await self._command_sender(
                "search_polyhaven_assets",
                {"asset_type": str(request.asset_type) if request.asset_type else "all", "categories": request.categories},
            )

            assets: list[AssetMetadata] = []
            for asset_id, data in result.get("assets", {}).items():
                assets.append(
                    AssetMetadata(
                        id=AssetId(asset_id),
                        name=AssetName(data.get("name", asset_id)),
                        type=AssetType(str(data.get("type", "unknown"))),
                        provider=ProviderName(self.provider_name),
                        tags=cast(TagList, data.get("categories", [])),
                    )
                )
            return AssetSearchResponseVO(
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
            logger.error("Polyhaven search error: %s", e)
            raise ProviderError(str(e)) from e

    async def get_asset_details(self, asset_id: str) -> AssetMetadata | None:
        """Get detailed info for a Polyhaven asset."""
        try:
            result = await self._command_sender("get_polyhaven_asset_details", {"asset_id": asset_id})
            if isinstance(result, dict) and "error" in result:
                logger.warning("Polyhaven get_asset_details error: %s", result["error"])
                return None
            tags = cast(TagList, result.get("tags", []) + result.get("categories", []))
            return AssetMetadata(
                id=AssetId(asset_id),
                name=AssetName(result.get("name", asset_id)),
                type=AssetType(result.get("type", "unknown")),
                provider=ProviderName(self.provider_name),
                tags=tags,
            )
        except Exception as e:
            logger.error("Polyhaven details error: %s", e)
            return None

    async def download_asset(self, request: AssetDownloadRequestVO) -> AssetDownloadResponseVO:
        try:
            asset_type = "models"
            result = await self._command_sender(
                "download_polyhaven_asset", {"asset_id": str(request.asset_id), "asset_type": asset_type}
            )
            if not result.get("success"):
                raise ProviderError(result.get("message", "Download failed"))
            return AssetDownloadResponseVO(
                success=SuccessFlag(True),
                file_path=FilePath(str(result.get("path", ""))),
                message=ErrorMessage("Download successful"),  # type: ignore[arg-type]
            )
        except Exception as e:
            logger.error("Polyhaven download error: %s", e)
            raise ProviderError(str(e)) from e
