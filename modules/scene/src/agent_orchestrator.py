"""Agent: Scene feature orchestrator.

Coordinates scene info, cleanup, and environment setup.
"""

import logging
from typing import Any

from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol
from modules.shared.src.scene.taxonomy_scene_request_vo import (
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)

logger = logging.getLogger("BlenderMCPServer")


class SceneOrchestrator:
    """Orchestrates scene operations."""

    def __init__(self, executor: SceneOperateProtocol):
        self._executor = executor

    async def get_scene_info(self, request: GetSceneInfoRequestVO) -> GetSceneInfoResponseVO:
        return await self._executor.get_scene_info(request)

    async def cleanup_scene(self, request: CleanupSceneRequestVO) -> CleanupSceneResponseVO:
        return await self._executor.cleanup_scene(request)

    async def setup_environment(self, request: SetupEnvironmentRequestVO) -> SetupEnvironmentResponseVO:
        return await self._executor.setup_environment(request)
