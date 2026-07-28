"""Scene taxonomy events."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.taxonomy_core_vo import (
    CleanupMode,
    ObjectCount,
    Prompt,
    RequestId,
    SuccessFlag,
)
from .taxonomy_scene_error import SceneErrorCategory


@dataclass(frozen=True)
class SceneInspectionCompletedEvent:
    """Emitted when scene inspection completes successfully."""

    correlation_id: RequestId
    success: SuccessFlag
    detail_level: str
    total_object_count: ObjectCount
    message: Prompt


@dataclass(frozen=True)
class SceneCleanupCompletedEvent:
    """Emitted when actual cleanup completes."""

    correlation_id: RequestId
    success: SuccessFlag
    mode: CleanupMode
    removed_count: ObjectCount
    preserved_count: ObjectCount
    skipped_count: ObjectCount
    message: Prompt


@dataclass(frozen=True)
class SceneCleanupDryRunCompletedEvent:
    """Emitted when dry-run cleanup preview completes."""

    correlation_id: RequestId
    success: SuccessFlag
    mode: CleanupMode
    removable_count: ObjectCount
    preserved_count: ObjectCount
    skipped_count: ObjectCount
    message: Prompt


@dataclass(frozen=True)
class SceneCleanupFailedEvent:
    """Emitted when cleanup fails or partially fails."""

    correlation_id: RequestId
    success: SuccessFlag
    mode: CleanupMode
    dry_run: bool
    error_category: SceneErrorCategory
    message: Prompt