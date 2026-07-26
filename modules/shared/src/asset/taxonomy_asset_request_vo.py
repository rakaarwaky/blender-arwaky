"""Asset search and download request/response value objects.

Re-exports merged VOs from taxonomy_asset_vo.py for backward compatibility.
"""

from .taxonomy_asset_vo import (
    AssetDownloadVO,
    AssetMetadataItem,
    AssetMetadataVO,
    AssetSearchVO,
)

# Legacy aliases — prefer the merged VO names above
AssetSearchRequestVO = AssetSearchVO
AssetSearchResponseVO = AssetSearchVO
AssetDownloadRequestVO = AssetDownloadVO
AssetDownloadResponseVO = AssetDownloadVO

__all__ = [
    "AssetDownloadVO",
    "AssetMetadataItem",
    "AssetMetadataVO",
    "AssetSearchVO",
]
