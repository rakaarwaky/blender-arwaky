"""Scene domain contract: scene aggregate.

Agent implements this aggregate.
Surface layers depend on this facade.
"""

from __future__ import annotations

from .contract_scene_cleanup_protocol import ISceneCleanupProtocol
from .contract_scene_inspection_protocol import ISceneInspectionProtocol
from .taxonomy_scene_vo import SceneOverviewVO


class ISceneAggregate(ISceneInspectionProtocol, ISceneCleanupProtocol):
    """Facade for scene feature behavior.

    Combines:
    - FR-SCN-001 inspection
    - FR-SCN-002 cleanup
    """

    _taxonomy_types = (SceneOverviewVO,)

