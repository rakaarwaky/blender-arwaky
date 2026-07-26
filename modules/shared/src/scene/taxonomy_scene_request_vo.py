"""Scene operation request and response value objects.

Re-exports merged VOs from taxonomy_scene_vo.py for backward compatibility.
Legacy Request/Response names point to the unified VO classes.
"""

from .taxonomy_scene_vo import (
    CleanupSceneVO,
    GetSceneInfoVO,
    SetupEnvironmentVO,
)

# Legacy request aliases
CleanupSceneRequestVO = CleanupSceneVO
GetSceneInfoRequestVO = GetSceneInfoVO
SetupEnvironmentRequestVO = SetupEnvironmentVO

# Legacy response aliases — ResponseVO is merged into the unified VO
CleanupSceneResponseVO = CleanupSceneVO
GetSceneInfoResponseVO = GetSceneInfoVO
SetupEnvironmentResponseVO = SetupEnvironmentVO

__all__ = [
    # Unified VO names
    "CleanupSceneVO",
    "GetSceneInfoVO",
    "SetupEnvironmentVO",
    # Legacy aliases
    "CleanupSceneRequestVO",
    "GetSceneInfoRequestVO",
    "SetupEnvironmentRequestVO",
    "CleanupSceneResponseVO",
    "GetSceneInfoResponseVO",
    "SetupEnvironmentResponseVO",
]
