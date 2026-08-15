"""Scene domain — FR-SCN-002: Cleanup scene objects."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_vo import SceneCleanupVO


class ISceneCleanupProtocol(ABC):
    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO: ...
