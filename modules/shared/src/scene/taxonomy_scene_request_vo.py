"""Scene operation request and response value objects."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    CleanupMode,
    ObjectCount,
    Prompt,
    SuccessFlag,
)


@dataclass(frozen=True)
class CleanupSceneRequestVO:
    """Request to clean up the scene."""

    mode: CleanupMode = field(default=CleanupMode("all"))


@dataclass(frozen=True)
class CleanupSceneResponseVO:
    """Response from a scene cleanup operation."""

    success: SuccessFlag
    objects_removed: ObjectCount
    message: Prompt


@dataclass(frozen=True)
class GetSceneInfoRequestVO:
    """Request to retrieve scene information."""

    pass


@dataclass(frozen=True)
class GetSceneInfoResponseVO:
    """Response containing scene information."""

    success: SuccessFlag
    scene_info: object  # SceneInfo or similar
    message: Prompt


@dataclass(frozen=True)
class SetupEnvironmentRequestVO:
    """Request to set up scene environment (HDRI, lighting)."""

    hdri_id: str
    strength: float = 1.0


@dataclass(frozen=True)
class SetupEnvironmentResponseVO:
    """Response from environment setup operation."""

    success: SuccessFlag
    hdri_path: str | None
    message: Prompt
