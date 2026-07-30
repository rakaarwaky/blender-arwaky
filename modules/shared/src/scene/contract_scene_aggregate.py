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
    - FR-SCN-001 inspection
    - FR-SCN-002 cleanup
    """

    @abstractmethod
    async def inspect_scene(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Facade method for FR-SCN-001 scene inspection."""
        ...

    @abstractmethod
    async def cleanup_scene_objects(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Facade method for FR-SCN-002 scene cleanup."""
        ...
