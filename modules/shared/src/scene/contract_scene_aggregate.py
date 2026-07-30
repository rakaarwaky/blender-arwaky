"""Scene domain contract: scene aggregate.

Agent implements this aggregate.
Surface layers depend on this facade.
"""

from __future__ import annotations

from abc import abstractmethod

from .contract_scene_cleanup_protocol import ISceneCleanupProtocol
from .contract_scene_inspection_protocol import ISceneInspectionProtocol
from .taxonomy_scene_vo import SceneCleanupVO, SceneInspectionVO


class ISceneAggregate(ISceneInspectionProtocol, ISceneCleanupProtocol):
    """Facade for scene feature behavior.

    Combines:
    - FR-SCN-001 inspection (get_scene_info)
    - FR-SCN-002 cleanup (cleanup_scene)
    """

    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """FR-SCN-001: Inspect scene state."""
        ...

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """FR-SCN-002: Cleanup scene objects."""
        ...
