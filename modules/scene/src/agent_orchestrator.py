"""Agent: Scene feature orchestrator.

Coordinates scene inspection and cleanup through the
SceneOperateProtocol capability layer.

FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate
from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort
from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol
from modules.shared.src.scene.taxonomy_scene_command_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)

if TYPE_CHECKING:
    from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort

logger = logging.getLogger("BlenderMCPServer")


class SceneOrchestrator:
    """Orchestrates scene operations via capability protocols.

    FR-SCN-001, FR-SCN-002: Enhanced with preservation policy, dry-run, child/dependent handling.
    Unified VO (merged request + response) — no split classes.
    """

    def __init__(
        self,
        executor: SceneOperateProtocol,
        inspector: SceneInspectionPort | None = None,
    ) -> None:
        self._executor = executor
        self._inspector = inspector

    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Retrieve current scene metadata and object tree.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        return await self._executor.get_scene_info(request)

    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup of scene objects based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        return await self._executor.cleanup_scene(request)

    async def get_scene_info_via_inspector(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Retrieve scene info via inspection port (fallback path).

        FR-SCN-001: Supports detail level, hidden objects filter.
        """
        if self._inspector is not None:
            return await self._inspector.get_scene_info(request)
        raise RuntimeError("No inspector available")

    async def cleanup_scene_via_inspector(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup via inspection port (fallback path).

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        """
        if self._inspector is not None:
            return await self._inspector.cleanup_scene(request)
        raise RuntimeError("No inspector available")
