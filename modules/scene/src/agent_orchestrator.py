"""Agent: Scene feature orchestrator.

Coordinates scene info, cleanup, and environment setup through the
SceneOperateProtocol capability layer.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol
from modules.shared.src.scene.taxonomy_scene_request_vo import (
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)

if TYPE_CHECKING:
    from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort

logger = logging.getLogger("BlenderMCPServer")


class SceneOrchestrator:
    """Orchestrates scene operations via capability protocols."""

    def __init__(
        self,
        executor: SceneOperateProtocol,
        inspector: SceneInspectionPort | None = None,
    ) -> None:
        self._executor = executor
        self._inspector = inspector

    async def get_scene_info(self, request: GetSceneInfoRequestVO) -> GetSceneInfoResponseVO:
        return await self._executor.get_scene_info(request)

    async def cleanup_scene(self, request: CleanupSceneRequestVO) -> CleanupSceneResponseVO:
        return await self._executor.cleanup_scene(request)

    async def setup_environment(
        self, request: SetupEnvironmentRequestVO
    ) -> SetupEnvironmentResponseVO:
        return await self._executor.setup_environment(request)
