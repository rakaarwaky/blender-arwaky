"""Agent: Scene orchestrator.

Coordinates scene capabilities through contracts only.

Agent layer:
- orchestration only
- zero I/O
- zero business logic
- zero domain computation
- depends only on contracts and taxonomy
"""

from __future__ import annotations

from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate
from modules.shared.src.scene.contract_scene_cleanup_protocol import ISceneCleanupProtocol
from modules.shared.src.scene.contract_scene_inspection_protocol import ISceneInspectionProtocol
from modules.shared.src.scene.taxonomy_scene_vo import SceneCleanupVO, SceneInspectionVO


class SceneOrchestrator(ISceneAggregate):
    """Orchestrates scene inspection and cleanup capabilities."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(
        self,
        inspection: ISceneInspectionProtocol,
        cleanup: ISceneCleanupProtocol,
    ) -> None:
        self._inspection = inspection
        self._cleanup = cleanup

    # ─── Block 2: aggregate methods only ──────────────────────
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """FR-SCN-001: delegate to inspection capability."""
        return await self._inspection.get_scene_info(request)

    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """FR-SCN-002: delegate to cleanup capability."""
        return await self._cleanup.cleanup_scene(request)

    # ─── Block 3: dunders / factories / helpers ───────────────
    def __repr__(self) -> str:
        return "SceneOrchestrator()"