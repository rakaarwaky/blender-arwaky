"""Asset operation value objects — unified input/output per operation.

Each VO merges request (input) and response (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from modules.shared.src.common.taxonomy_core_vo import (
    AssetCount,
    AssetId,
    AssetName,
    AssetType,
    ErrorMessage,
    FilePath,
    ObjectName,
    ProviderName,
    SearchQuery,
    SuccessFlag,
    TagList,
    ThumbnailUrl,
)


@dataclass(frozen=True)
class AssetMetadataItem:
    """Individual asset metadata item from search results."""

    id: AssetId
    name: AssetName
    type: AssetType
    provider: ProviderName
    thumbnail_url: ThumbnailUrl | None = None
    tags: TagList = field(default_factory=lambda: TagList([]))


AssetMetadataVO = AssetMetadataItem


@dataclass(frozen=True)
class AssetSearchVO:
    """Asset search — input and output in one VO.

    Input: query.
    Output: assets, total, next_token, provider.
    """
    # Input
    query: SearchQuery
    # Output
    assets: list[AssetMetadataItem] = field(default_factory=list)
    total: AssetCount | None = None
    next_token: str | None = None
    provider: ProviderName | None = None


@dataclass(frozen=True)
class AssetDownloadVO:
    """Asset download — input and output in one VO.

    Input: asset_id, destination_path.
    Output: success, file_path, message.
    """
    # Input
    asset_id: AssetId
    destination_path: FilePath
    # Output
    success: SuccessFlag | None = None
    file_path: FilePath | None = None
    message: ErrorMessage | None = None


@dataclass(frozen=True)
class ImportGlbVO:
    """Import GLB — input and output in one VO.

    Input: file_path, object_name.
    Output: success, object_name, message.
    """
    # Input
    file_path: str
    object_name: ObjectName | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class ExportModelVO:
    """Export model — input and output in one VO.

    Input: object_name, file_path, export_format.
    Output: success, message.
    """
    # Input
    object_name: ObjectName
    file_path: str
    export_format: str | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""
