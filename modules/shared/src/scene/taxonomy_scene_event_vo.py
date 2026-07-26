"""Scene domain event value objects — taxonomy events.

Event types for scene management operations:
- SceneInspectionCompletedEvent: emitted after scene inspection successfully produces scene state summary
- SceneCleanupCompletedEvent: emitted after actual cleanup operation finishes and cleanup report is produced
- SceneCleanupDryRunCompletedEvent: emitted after dry-run preview finishes and preview report is produced
- SceneCleanupFailedEvent: emitted when cleanup operation fails or partially fails

Event payloads include: operation type, success indicator, summary counts,
dry-run indicator, error category when failed, correlation identifier when available.
Event payloads avoid full object dumps for large scenes and must avoid sensitive data.

FR-SCN-001, FR-SCN-002: Events
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SceneInspectionCompletedEvent:
    """Event emitted after scene inspection successfully produces scene state summary.

    FR-SCN-001: scene inspection completed event.
    """

    operation: str = "scene_inspection_completed"
    success: bool = False
    object_count: int = 0
    camera_count: int = 0
    light_count: int = 0
    dry_run: bool = False
    error_category: str = ""
    correlation_id: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class SceneCleanupCompletedEvent:
    """Event emitted after actual cleanup operation finishes and cleanup report is produced.

    FR-SCN-002: scene cleanup completed event.
    """

    operation: str = "scene_cleanup_completed"
    success: bool = False
    removed_count: int = 0
    preserved_count: int = 0
    skipped_count: int = 0
    dry_run: bool = False
    error_category: str = ""
    correlation_id: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class SceneCleanupDryRunCompletedEvent:
    """Event emitted after dry-run preview finishes and preview report is produced.

    FR-SCN-002: scene cleanup dry-run completed event.
    """

    operation: str = "scene_cleanup_dry_run_completed"
    success: bool = False
    removed_count: int = 0
    preserved_count: int = 0
    skipped_count: int = 0
    dry_run: bool = True
    error_category: str = ""
    correlation_id: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class SceneCleanupFailedEvent:
    """Event emitted when cleanup operation fails or partially fails.

    FR-SCN-002: scene cleanup failed event.
    """

    operation: str = "scene_cleanup_failed"
    success: bool = False
    removed_count: int = 0
    preserved_count: int = 0
    skipped_count: int = 0
    dry_run: bool = False
    error_category: str = ""
    correlation_id: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)
