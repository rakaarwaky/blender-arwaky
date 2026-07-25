"""Scene domain contract: scene operations protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_request_vo import (
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)


class SceneOperateProtocol(ABC):
    """Protocol interface for scene-level management (cleanup, environment, metadata)."""

    @abstractmethod
    async def cleanup_scene(
        self, request: CleanupSceneRequestVO
    ) -> CleanupSceneResponseVO:
        """Remove objects and reset scene state."""
        pass

    @abstractmethod
    async def setup_environment(
        self, request: SetupEnvironmentRequestVO
    ) -> SetupEnvironmentResponseVO:
        """Set HDRI and world environment properties."""
        pass

    @abstractmethod
    async def get_scene_info(
        self, request: GetSceneInfoRequestVO
    ) -> GetSceneInfoResponseVO:
        """Retrieve current scene metadata and object tree."""
        pass
