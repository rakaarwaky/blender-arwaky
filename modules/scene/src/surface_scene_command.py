"""Surface: Scene command.

Public entry point for scene feature operations.
Delegates to ISceneAggregate (Contract layer).
"""

from __future__ import annotations

from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate
from modules.shared.src.scene.taxonomy_scene_vo import SceneCleanupVO, SceneInspectionVO


class SceneCommand:
    """Surface command exposing scene operations to external callers."""

    # ─── Block 1: definition + constructor ─────────────
    def __init__(self, aggregate: ISceneAggregate) -> None:
        self._aggregate = aggregate

    # ─── Block 2: surface methods only ──────────────
    async def inspect(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Public inspection API — delegates to aggregate."""
        return await self._aggregate.get_scene_info(request)

    async def cleanup(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Public cleanup API — delegates to aggregate."""
        return await self._aggregate.cleanup_scene(request)

    # ─── Block 3: dunders / factories / helpers ───────
    def __repr__(self) -> str:
        return "SceneCommand()"
