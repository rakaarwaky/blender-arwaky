"""Scene domain — taxonomy types and contracts.

Unified VOs (merged request + response — no split classes). No legacy Request/Response aliases.
"""

from .contract_scene_cleanup_protocol import SceneCleanupProtocol
from .contract_scene_inspection import SceneInspectionPort
from .contract_scene_operate_protocol import SceneOperateProtocol
from .taxonomy_scene_command_vo import (
    CameraInfoVO,
    CollectionSummaryVO,
    LightInfoVO,
    ProtectedObjectSummaryVO,
    SceneCleanupVO,
    SceneInspectionVO,
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
from .taxonomy_scene_info_vo import SceneInfo

__all__ = [
    # Protocols
    "SceneInspectionPort",
    "SceneCleanupProtocol",
    "SceneOperateProtocol",
    # Unified VOs (merged request + response — no split classes)
    "SceneCleanupVO",
    "SceneInspectionVO",
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
    # Legacy
    "SceneInfo",
]
