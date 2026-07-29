"""Asset operation value objects — unified input/output per operation.

Each VO merges request (input) and response (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from modules.shared.src.common.taxonomy_core_vo import (
    AssetCollectionName,
    AssetCount,
    AssetFormatHint,
    AssetId,
    AssetName,
    AssetType,
    ErrorMessage,
    FilePath,
    MaxSize,
    ObjectName,
    ProviderName,
    ResolutionPreference,
    ScaleNormalization,
    SearchQuery,
    SuccessFlag,
    TagList,
    ThumbnailUrl,
)

__all__ = [
    "AssetCollectionName",
    "AssetFormatHint",
    "ScaleNormalization",
]


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


@dataclass(frozen=True)
class AssetDownloadCacheVO:
    """Asset download to cache — input and output in one VO.

    FR-AST-002: Download file to cache with integrity verification.
    Input: provider, asset_id, asset_type, cache_dir, resolution, overwrite_policy.
    Output: success, file_path, file_size, cached, integrity_ok, message.
    """

    # Input
    provider: ProviderName
    asset_id: AssetId
    asset_type: AssetType
    cache_dir: FilePath
    resolution: ResolutionPreference | None = None
    overwrite_policy: str = "reuse"
    max_size: MaxSize | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    file_path: FilePath | None = None
    file_size: int = 0
    cached: bool = False
    integrity_ok: bool = True
    message: str = ""
    error: ErrorMessage | None = None


@dataclass(frozen=True)
class AssetExtractArchiveVO:
    """Archive extraction — input and output in one VO.

    FR-AST-003: Extract downloaded archive under security supervision.
    Input: artifact_path, destination, max_entries, max_extracted_size, allow_symlinks.
    Output: success, extracted_files, rejected_entries, message.
    """

    # Input
    artifact_path: FilePath
    destination: FilePath
    max_entries: int = 1000
    max_extracted_size: int = 1073741824
    allow_symlinks: bool = False
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    extracted_files: tuple[FilePath, ...] = field(default_factory=tuple)
    rejected_entries: tuple[str, ...] = field(default_factory=tuple)
    message: str = ""
    error: ErrorMessage | None = None


@dataclass(frozen=True)
class AssetImportBlenderVO:
    """Import asset into Blender — input and output in one VO.

    FR-AST-004: Import locally available asset file into Blender.
    Input: file_path, asset_type, target_collection, scale_normalization, duplicate_policy.
    Output: success, object_names, asset_name, license_summary, message.
    """

    # Input
    file_path: FilePath
    asset_type: AssetType
    target_collection: str | None = None
    scale_normalization: bool = False
    duplicate_policy: str = "rename"
    format_hint: str | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    object_names: tuple[ObjectName, ...] = field(default_factory=tuple)
    asset_name: AssetName | None = None
    license_summary: str | None = None
    message: str = ""
    error: ErrorMessage | None = None


@dataclass(frozen=True)
class SearchResultVO:
    """Asset search result — normalized aggregated results with provider status.

    FR-AST-001: Unified search across providers returns normalized,
    aggregated results with provider status summary and warnings.
    Input: query (set via caller). Output: assets, total, provider_status, warnings.
    """

    # Output
    assets: list[AssetMetadataItem] = field(default_factory=list)
    total: AssetCount | None = None
    provider_status: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArchiveEntryVO:
    """Archive entry for security review (shared with security feature).

    FR-AST-003: Used by AssetExtractCapability to enumerate archive entries
    for the security supervisor. Replaces direct import of security taxonomy.
    """

    entry_path: str
    is_directory: bool = False
    is_symbolic_link: bool = False
    is_hard_link: bool = False
    compressed_size: int = 0
    uncompressed_size: int = 0


@dataclass(frozen=True)
class ArchiveExtractionOptionsVO:
    """Options for archive extraction validation.

    FR-AST-003: Passed to security supervisor via ArchiveExtractionVO.
    Fields match security taxonomy to ensure protocol compatibility.
    """

    max_depth: int = 5
    max_total_size: int = 104_857_600  # 100 MB
    max_entry_size: int = 10_485_760  # 10 MB
    max_entry_count: int = 1_000
    allow_symbolic_links: bool = False
    allow_hard_links: bool = False


@dataclass(frozen=True)
class ArchiveExtractionVO:
    """Request to validate archive extraction.

    FR-AST-003: Contains entries and options for the security supervisor.
    Replaces direct import of security taxonomy VOs.
    """

    destination_directory: str
    entries: tuple[ArchiveEntryVO, ...]
    options: ArchiveExtractionOptionsVO
