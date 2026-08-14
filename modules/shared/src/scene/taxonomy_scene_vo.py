"""Scene taxonomy value objects.

Unified request/response VOs per operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    CleanupMode,
    CoordinateList,
    ObjectCount,
    ObjectName,
    ObjectType,
    Prompt,
    RenderEngine,
    RequestId,
    ResolutionX,
    ResolutionY,
    RotationVector,
    ScaleVector,
    SceneId,
    SuccessFlag,
)
from .taxonomy_scene_constant import (
    CLEANUP_MODE_ALL,
    DEFAULT_CHILD_HANDLING_POLICY,
    DEFAULT_DEPENDENT_HANDLING_POLICY,
    DEFAULT_DRY_RUN_MODE,
    DEFAULT_FRAME_END,
    DEFAULT_FRAME_START,
    DEFAULT_FRAME_STEP,
    DEFAULT_INCLUDE_HIDDEN_OBJECTS,
    DEFAULT_PRESERVATION_LIST,
    DETAIL_LEVEL_STANDARD,
    PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA,
    PROTECTED_OBJECT_POLICY_SOLE_CAMERA,
)


# ─── Summary VOs ─────────────────────────────────────────────
@dataclass(frozen=True)
class CameraInfoVO:
    """Camera summary item."""

    name: ObjectName = field(default_factory=lambda: ObjectName(""))
    type: ObjectType = field(default_factory=lambda: ObjectType("CAMERA"))
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector = field(default_factory=lambda: RotationVector([0.0, 0.0, 0.0]))
    scale: ScaleVector = field(default_factory=lambda: ScaleVector([1.0, 1.0, 1.0]))
    data_type: str = ""
    sensor_width: float = 36.0
    focal_length: float = 50.0


@dataclass(frozen=True)
class LightInfoVO:
    """Light summary item."""

    name: ObjectName = field(default_factory=lambda: ObjectName(""))
    type: ObjectType = field(default_factory=lambda: ObjectType("LIGHT"))
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector = field(default_factory=lambda: RotationVector([0.0, 0.0, 0.0]))
    scale: ScaleVector = field(default_factory=lambda: ScaleVector([1.0, 1.0, 1.0]))
    light_type: str = ""
    strength: float = 1.0
    color: CoordinateList = field(default_factory=lambda: CoordinateList([1.0, 1.0, 1.0]))


@dataclass(frozen=True)
class CollectionSummaryVO:
    """Collection summary item."""

    name: ObjectName = field(default_factory=lambda: ObjectName(""))
    object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    child_collection_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    child_collections: tuple[ObjectName, ...] = ()


@dataclass(frozen=True)
class ProtectedObjectSummaryVO:
    """Protected object summary."""

    active_camera_name: ObjectName = field(default_factory=lambda: ObjectName(""))
    sole_camera_name: ObjectName = field(default_factory=lambda: ObjectName(""))
    light_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    protected_objects: tuple[ObjectName, ...] = ()


@dataclass(frozen=True)
class SceneStateSummaryVO:
    """Comprehensive scene state summary."""

    scene_name: str = ""
    scene_identifier: SceneId = field(default_factory=lambda: SceneId(""))

    total_object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    visible_object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    hidden_object_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    object_type_counts: dict[ObjectType, ObjectCount] = field(default_factory=dict)

    cameras: tuple[CameraInfoVO, ...] = ()
    lights: tuple[LightInfoVO, ...] = ()

    active_camera_name: ObjectName = field(default_factory=lambda: ObjectName(""))
    active_object_name: ObjectName = field(default_factory=lambda: ObjectName(""))

    render_engine: RenderEngine = field(default_factory=lambda: RenderEngine("CYCLES"))
    resolution_x: ResolutionX = field(default_factory=lambda: ResolutionX(1920))
    resolution_y: ResolutionY = field(default_factory=lambda: ResolutionY(1080))
    frame_start: int = field(default=DEFAULT_FRAME_START)
    frame_end: int = field(default=DEFAULT_FRAME_END)
    frame_step: int = field(default=DEFAULT_FRAME_STEP)
    unit_system: str = "METRIC"

    collection_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    collections: tuple[CollectionSummaryVO, ...] = ()

    protected_object_summary: ProtectedObjectSummaryVO = field(default_factory=ProtectedObjectSummaryVO)
    capability_flags: dict[str, bool] = field(default_factory=dict)
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── Unified operation VOs ───────────────────────────────────
@dataclass(frozen=True)
class SceneInspectionVO:
    """Scene inspection input/output VO."""

    # Input
    detail_level: str = DETAIL_LEVEL_STANDARD
    include_hidden_objects: bool = DEFAULT_INCLUDE_HIDDEN_OBJECTS
    object_type_filter: tuple[ObjectType, ...] = ()
    correlation_id: RequestId = field(default_factory=lambda: RequestId(""))

    # Output
    success: SuccessFlag = field(default_factory=lambda: SuccessFlag(False))
    scene_state_summary: SceneStateSummaryVO | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class SceneCleanupPolicyVO:
    """Resolved cleanup policy used by code builder utility."""

    mode: CleanupMode = field(default_factory=lambda: CleanupMode(CLEANUP_MODE_ALL))
    preserve_cameras: bool = True
    preserve_lights: bool = True
    include_hidden_objects: bool = DEFAULT_INCLUDE_HIDDEN_OBJECTS
    child_handling_policy: str = DEFAULT_CHILD_HANDLING_POLICY
    dependent_handling_policy: str = DEFAULT_DEPENDENT_HANDLING_POLICY
    protect_active_camera: bool = PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA
    protect_sole_camera: bool = PROTECTED_OBJECT_POLICY_SOLE_CAMERA


@dataclass(frozen=True)
class SceneCleanupMetricsVO:
    """Internal cleanup result metrics parsed from execution output."""

    removed_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    preserved_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    skipped_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    removed_object_references: tuple[ObjectName, ...] = ()
    preserved_object_references: tuple[ObjectName, ...] = ()
    skipped_object_references: tuple[ObjectName, ...] = ()


@dataclass(frozen=True)
class SceneCleanupVO:
    """Scene cleanup input/output VO.

    Expresses both success and partial-failure outcomes.
    error_summary is set when cleanup encounters errors (FRD observability gap fix).
    """

    # Input
    mode: CleanupMode = field(default_factory=lambda: CleanupMode(CLEANUP_MODE_ALL))
    preservation_list: tuple[str, ...] = field(default_factory=lambda: DEFAULT_PRESERVATION_LIST)
    dry_run: bool = DEFAULT_DRY_RUN_MODE
    confirmation: bool = False
    child_handling_policy: str = DEFAULT_CHILD_HANDLING_POLICY
    dependent_handling_policy: str = DEFAULT_DEPENDENT_HANDLING_POLICY
    include_hidden_objects: bool = DEFAULT_INCLUDE_HIDDEN_OBJECTS
    correlation_id: RequestId = field(default_factory=lambda: RequestId(""))

    # Output
    success: SuccessFlag = field(default_factory=lambda: SuccessFlag(False))
    removed_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    preserved_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    skipped_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    removed_object_references: tuple[ObjectName, ...] = ()
    preserved_object_references: tuple[ObjectName, ...] = ()
    skipped_object_references: tuple[ObjectName, ...] = ()
    error_summary: str | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))
