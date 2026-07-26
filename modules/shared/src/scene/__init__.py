"""Scene domain — taxonomy types and contracts."""

from .contract_scene_cleanup_protocol import SceneCleanupProtocol
from .contract_scene_inspection import SceneInspectionPort
from .contract_scene_operate_protocol import SceneOperateProtocol
from .taxonomy_scene_info_vo import SceneInfo
from .taxonomy_scene_request_vo import (
    CleanupRequestVO,
    CleanupReportVO,
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    CleanupPreviewVO,
    InspectionRequestVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)

# Enhanced VOs
from .taxonomy_scene_request_vo import (
    CameraInfoVO,
    CollectionSummaryVO,
    LightInfoVO,
    ProtectedObjectSummaryVO,
    SceneStateSummaryVO,
)

# Error VOs
from .taxonomy_scene_error_vo import (
    CleanupTimeoutError,
    ConfirmationError,
    ConnectionError,
    DelegatedDeletionError,
    ProtectionError,
    SceneStateError,
    ValidationError,
)

# Event VOs
from .taxonomy_scene_event_vo import (
    SceneCleanupCompletedEvent,
    SceneCleanupDryRunCompletedEvent,
    SceneCleanupFailedEvent,
    SceneInspectionCompletedEvent,
)

__all__ = [
    # Protocols
    "SceneInspectionPort",
    "SceneCleanupProtocol",
    "SceneOperateProtocol",
    # Legacy Request/Response VOs
    "SceneInfo",
    "CleanupSceneRequestVO",
    "CleanupSceneResponseVO",
    "GetSceneInfoRequestVO",
    "GetSceneInfoResponseVO",
    "SetupEnvironmentRequestVO",
    "SetupEnvironmentResponseVO",
    # Enhanced Request VOs
    "CleanupRequestVO",
    "InspectionRequestVO",
    # Enhanced Report/Response VOs
    "CleanupReportVO",
    "CleanupPreviewVO",
    # Scene State Summary VOs
    "CameraInfoVO",
    "LightInfoVO",
    "CollectionSummaryVO",
    "ProtectedObjectSummaryVO",
    "SceneStateSummaryVO",
    # Error VOs
    "SceneStateError",
    "ProtectionError",
    "ValidationError",
    "ConfirmationError",
    "DelegatedDeletionError",
    "CleanupTimeoutError",
    "ConnectionError",
    # Event VOs
    "SceneInspectionCompletedEvent",
    "SceneCleanupCompletedEvent",
    "SceneCleanupDryRunCompletedEvent",
    "SceneCleanupFailedEvent",
]
