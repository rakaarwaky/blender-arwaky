"""Scene operation request and response value objects — comprehensive VOs.

Enhanced VOs per FRD:
- CleanupRequestVO: cleanup request with preservation policy, dry-run, child/dependent handling
- CleanupReportVO: cleanup report with removed/preserved/skipped counts and references
- InspectionRequestVO: inspection request with detail level, hidden objects filter, summary mode
- SceneStateSummaryVO: comprehensive scene state summary
- CameraInfoVO: camera object information
- LightInfoVO: light object information
- CollectionSummaryVO: collection summary
- ProtectedObjectSummaryVO: protected object summary

Backward-compatible legacy aliases maintained.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..common.taxonomy_core_vo import (
    BlenderObjectList,
    CleanupMode,
    CoordinateList,
    ObjectCount,
    ObjectId,
    ObjectType,
    Prompt,
    ResolutionX,
    ResolutionY,
    ScaleVector,
    SuccessFlag,
    RotationVector,
)


# ─── Request VOs ──────────────────────────────────────────────


@dataclass(frozen=True)
class CleanupRequestVO:
    """Scene cleanup request with preservation policy and handling options.

    Input: mode, preservation list, dry-run flag, confirmation flag,
    child handling policy, dependent handling policy, protected object policy.
    """
    # Input fields
    mode: CleanupMode = field(default=CleanupMode("all"))
    preservation_list: tuple[str, ...] = ()
    dry_run: bool = False
    confirmation: bool = False
    child_handling_policy: str = "detach"  # "delete", "detach", "reject"
    dependent_handling_policy: str = "reject"  # "ignore", "reject", "remove_safe"
    include_hidden_objects: bool = False
    correlation_id: str = ""

    # Output fields (set by capability)
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class InspectionRequestVO:
    """Scene inspection request with detail level and filters.

    Input: detail level, hidden objects filter, summary mode, object type filter.
    """
    # Input fields
    detail_level: str = "standard"  # "minimal", "standard", "detailed", "summary"
    include_hidden_objects: bool = False
    object_type_filter: tuple[str, ...] = ()
    correlation_id: str = ""

    # Output fields (set by capability)
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class GetSceneInfoRequestVO:
    """Legacy request VO for backward compatibility.

    Input: (none).
    Output: scene_info dict.
    """
    pass


# ─── Report/Response VOs ──────────────────────────────────────


@dataclass(frozen=True)
class CleanupReportVO:
    """Scene cleanup report with detailed counts and references.

    Output: success, removed/preserved/skipped counts and references,
    dry-run indicator, message. Same structure for both actual cleanup
    and dry-run preview.
    """
    # Output fields
    success: SuccessFlag = field(default=SuccessFlag(False))
    removed_count: ObjectCount = 0
    preserved_count: ObjectCount = 0
    skipped_count: ObjectCount = 0
    removed_object_references: list[str] = field(default_factory=list)
    preserved_object_references: list[str] = field(default_factory=list)
    skipped_object_references: list[str] = field(default_factory=list)
    dry_run: bool = False
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class CleanupPreviewVO(CleanupReportVO):
    """Dry-run cleanup preview — same structure as CleanupReportVO.

    Inherits from CleanupReportVO with dry_run=True by default.
    """
    dry_run: bool = True


@dataclass(frozen=True)
class GetSceneInfoResponseVO:
    """Legacy response VO for backward compatibility.

    Output: success, scene_info dict, message.
    """
    success: SuccessFlag = field(default=SuccessFlag(False))
    scene_info: dict[str, Any] | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── Scene State Summary VOs ──────────────────────────────────


@dataclass(frozen=True)
class CameraInfoVO:
    """Camera object information.

    Output: object name, type, location, rotation, scale, data properties.
    """
    name: str = ""
    type: ObjectType = field(default_factory=lambda: ObjectType("CAMERA"))
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector = field(default_factory=lambda: RotationVector([0.0, 0.0, 0.0]))
    scale: ScaleVector = field(default_factory=lambda: ScaleVector([1.0, 1.0, 1.0]))
    data_type: str = ""  # e.g., "perspective", "orthographic"
    sensor_width: float = 36.0
    focal_length: float = 50.0


@dataclass(frozen=True)
class LightInfoVO:
    """Light object information.

    Output: object name, type, location, rotation, scale, data properties.
    """
    name: str = ""
    type: ObjectType = field(default_factory=lambda: ObjectType("LIGHT"))
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector = field(default_factory=lambda: RotationVector([0.0, 0.0, 0.0]))
    scale: ScaleVector = field(default_factory=lambda: ScaleVector([1.0, 1.0, 1.0]))
    light_type: str = ""  # e.g., "point", "spot", "area", "sun"
    strength: float = 1.0
    color: CoordinateList = field(default_factory=lambda: CoordinateList([1.0, 1.0, 1.0]))


@dataclass(frozen=True)
class CollectionSummaryVO:
    """Collection summary with object counts and structure.

    Output: collection name, object count, child collections.
    """
    name: str = ""
    object_count: ObjectCount = 0
    child_collection_count: ObjectCount = 0
    child_collections: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProtectedObjectSummaryVO:
    """Protected object summary with protection reasons.

    Output: protected objects and their protection categories.
    """
    active_camera_name: str = ""
    sole_camera_name: str = ""
    light_count: ObjectCount = 0
    protected_objects: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SceneStateSummaryVO:
    """Comprehensive scene state summary.

    FR-SCN-001: Scene state summary includes object count, camera list,
    light list, render settings, collection summary, protected object summary.
    Object list is deterministic, ordered by stable object reference.
    """
    # Scene metadata
    scene_name: str = ""
    scene_identifier: str = ""

    # Object counts
    total_object_count: ObjectCount = 0
    visible_object_count: ObjectCount = 0
    hidden_object_count: ObjectCount = 0
    object_type_counts: dict[str, ObjectCount] = field(default_factory=dict)

    # Camera and light summaries
    cameras: list[CameraInfoVO] = field(default_factory=list)
    lights: list[LightInfoVO] = field(default_factory=list)

    # Active references
    active_camera_name: str = ""
    active_object_name: str = ""

    # Render settings
    render_engine: str = "CYCLES"
    resolution_x: ResolutionX = ResolutionX(1920)
    resolution_y: ResolutionY = ResolutionY(1080)
    frame_start: int = 1
    frame_end: int = 250
    frame_step: int = 1
    unit_system: str = "METRIC"

    # Collections
    collection_count: ObjectCount = 0
    collections: list[CollectionSummaryVO] = field(default_factory=list)

    # Protected objects
    protected_object_summary: ProtectedObjectSummaryVO = field(default_factory=ProtectedObjectSummaryVO)

    # Capability flags
    capability_flags: dict[str, bool] = field(default_factory=dict)

    # Message
    message: str = ""
