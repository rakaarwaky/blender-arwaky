"""Scene domain — FR-SCN-001: Inspect scene state."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_vo import SceneInspectionVO


class ISceneInspectionProtocol(ABC):
    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO: ...
