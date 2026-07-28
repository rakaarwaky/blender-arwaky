"""Scene domain shared contracts, taxonomy, and utilities."""

from .contract_scene_aggregate import ISceneAggregate
from .contract_scene_protocol import ISceneCleanupProtocol, ISceneInspectionProtocol

from .taxonomy_scene_constant import (
    CHILD_POLICY_DELETE,
    CHILD_POLICY_DETACH,
    CHILD_POLICY_REJECT,
    CLEANUP_CONFIRMATION_REQUIRED,
    CLEANUP_MODE_ALL,
    CLEANUP_MODE_MESHES,
    CLEANUP_MODE_OBJECTS,
    CLEANUP_TIMEOUT_SECONDS,
    DEFAULT_CHILD_HANDLING_POLICY,
    DEFAULT_DEPENDENT_HANDLING_POLICY,
    DEFAULT_DRY_RUN_MODE,
    DEFAULT_INCLUDE_HIDDEN_OBJECTS,
    DEFAULT_PRESERVATION_LIST,
    DEPENDENT_POLICY_IGNORE,
    DEPENDENT_POLICY_REJECT,
    DEPENDENT_POLICY_REMOVE_SAFE,
    DETAIL_LEVEL_DETAILED,
    DETAIL_LEVEL_MINIMAL,
    DETAIL_LEVEL_STANDARD,
    DETAIL_LEVEL_SUMMARY,
    INSPECTION_TIMEOUT_SECONDS,
    MAX_INSPECTION_DETAIL_LIMIT,
    OBJECT_TYPE_CAMERA,
    OBJECT_TYPE_LIGHT,
    OBJECT_TYPE_MESH,
    PRESERVATION_CAMERA,
    PRESERVATION_LIGHT,
    PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA,
    PROTECTED_OBJECT_POLICY_LIGHTS,
    PROTECTED_OBJECT_POLICY_PROTECTED,
    PROTECTED_OBJECT_POLICY_SOLE_CAMERA,
    VALID_CHILD_HANDLING_POLICIES,
    VALID_CLEANUP_MODES,
    VALID_DEPENDENT_HANDLING_POLICIES,
    VALID_DETAIL_LEVELS,
)

from .taxonomy_scene_error import SceneError, SceneErrorCategory

from .taxonomy_scene_event import (
    SceneCleanupCompletedEvent,
    SceneCleanupDryRunCompletedEvent,
    SceneCleanupFailedEvent,
    SceneInspectionCompletedEvent,
)

from .taxonomy_scene_vo import (
    CameraInfoVO,
    CollectionSummaryVO,
    LightInfoVO,
    ProtectedObjectSummaryVO,
    SceneCleanupMetricsVO,
    SceneCleanupPolicyVO,
    SceneCleanupVO,
    SceneInspectionVO,
    SceneStateSummaryVO,
)

__all__ = [
    # Contracts
    "ISceneAggregate",
    "ISceneCleanupProtocol",
    "ISceneInspectionProtocol",

    # Constants
    "CHILD_POLICY_DELETE",
    "CHILD_POLICY_DETACH",
    "CHILD_POLICY_REJECT",
    "CLEANUP_CONFIRMATION_REQUIRED",
    "CLEANUP_MODE_ALL",
    "CLEANUP_MODE_MESHES",
    "CLEANUP_MODE_OBJECTS",
    "CLEANUP_TIMEOUT_SECONDS",
    "DEFAULT_CHILD_HANDLING_POLICY",
    "DEFAULT_DEPENDENT_HANDLING_POLICY",
    "DEFAULT_DRY_RUN_MODE",
    "DEFAULT_INCLUDE_HIDDEN_OBJECTS",
    "DEFAULT_PRESERVATION_LIST",
    "DEPENDENT_POLICY_IGNORE",
    "DEPENDENT_POLICY_REJECT",
    "DEPENDENT_POLICY_REMOVE_SAFE",
    "DETAIL_LEVEL_DETAILED",
    "DETAIL_LEVEL_MINIMAL",
    "DETAIL_LEVEL_STANDARD",
    "DETAIL_LEVEL_SUMMARY",
    "INSPECTION_TIMEOUT_SECONDS",
    "MAX_INSPECTION_DETAIL_LIMIT",
    "OBJECT_TYPE_CAMERA",
    "OBJECT_TYPE_LIGHT",
    "OBJECT_TYPE_MESH",
    "PRESERVATION_CAMERA",
    "PRESERVATION_LIGHT",
    "PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA",
    "PROTECTED_OBJECT_POLICY_LIGHTS",
    "PROTECTED_OBJECT_POLICY_PROTECTED",
    "PROTECTED_OBJECT_POLICY_SOLE_CAMERA",
    "VALID_CHILD_HANDLING_POLICIES",
    "VALID_CLEANUP_MODES",
    "VALID_DEPENDENT_HANDLING_POLICIES",
    "VALID_DETAIL_LEVELS",

    # Errors
    "SceneError",
    "SceneErrorCategory",

    # Events
    "SceneCleanupCompletedEvent",
    "SceneCleanupDryRunCompletedEvent",
    "SceneCleanupFailedEvent",
    "SceneInspectionCompletedEvent",

    # VOs
    "CameraInfoVO",
    "CollectionSummaryVO",
    "LightInfoVO",
    "ProtectedObjectSummaryVO",
    "SceneCleanupMetricsVO",
    "SceneCleanupPolicyVO",
    "SceneCleanupVO",
    "SceneInspectionVO",
    "SceneStateSummaryVO",
]