"""Scene domain contract: scene aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for scene operations: inspect, cleanup.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_command_vo import SceneCleanupVO, SceneInspectionVO


class ISceneAggregate(ABC):
    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        ...

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        ...
