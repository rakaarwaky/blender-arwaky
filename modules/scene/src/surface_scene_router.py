"""Surface: Scene router.

Public entry point for scene feature operations.
Delegates to SceneOrchestrator (Agent layer).
"""

from __future__ import annotations

from modules.scene.src.agent_scene_orchestrator import SceneOrchestrator
from modules.scene.src.taxonomy_scene_vo import SceneCleanupVO, SceneInspectionVO


class SceneRouter:
    """Surface router exposing scene operations to external callers."""

    # ─── Block 1: definition + constructor ─────────────
    def __init__(self, orchestrator: SceneOrchestrator) -> None:
        self._orchestrator = orchestrator

    # ─── Block 2: surface methods only ──────────────
    async def inspect(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Public inspection API — delegates to orchestrator."""
        return await self._orchestrator.get_scene_info(request)

    async def cleanup(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Public cleanup API — delegates to orchestrator."""
        return await self._orchestrator.cleanup_scene(request)

    # ─── Block 3: dunders / factories / helpers ───────────────
    def __repr__(self) -> str:
        return "SceneRouter()"
