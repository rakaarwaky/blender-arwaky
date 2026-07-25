"""
Executor: Complex multi-step workflow orchestration.

This is a capabilities-layer executor that coordinates across
multiple handlers and providers. It depends on other capabilities
but does so via constructor injection with port interfaces.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.shared.src.asset.contract_asset_search_protocol import AssetSearchProtocol
    from modules.shared.src.scene.contract_scene_operate_protocol import SceneOperateProtocol

from modules.shared.src.common.contract_workflow_protocol import WorkflowProtocol
from modules.shared.src.common.taxonomy_core_vo import HdriId, Prompt, PythonCode, SearchQuery, SuccessFlag
from modules.shared.src.common.taxonomy_domain_error import BlenderMCPError
from modules.shared.src.scene.taxonomy_scene_request_vo import CleanupSceneRequestVO, SetupEnvironmentRequestVO

logger = logging.getLogger("BlenderMCPServer")


class WorkflowExecutor(WorkflowProtocol):
    """Orchestrates multiple capabilities to perform high-level tasks."""

    def __init__(
        self,
        blender_executor: "SceneOperateProtocol",
        asset_collector: "AssetSearchProtocol",
    ):
        self.blender = blender_executor
        self.assets = asset_collector

    async def create_basic_scene(self, prompt: Prompt) -> SuccessFlag:
        """
        Workflow:
        1. Cleanup tool_scene_ops.
        2. Search for assets matching prompt.
        3. Place the first relevant asset.
        4. Setup a default environment.
        """
        logger.info(f"Creating basic scene for prompt: {prompt}")
        try:
            # 1. Cleanup
            await self.blender.cleanup_scene(CleanupSceneRequestVO())

            # 2. Search Assets
            assets = await self.assets.search_all(SearchQuery(str(prompt)))
            if not assets:
                logger.warning(f"No assets found for prompt: {prompt}")
                return SuccessFlag(False)

            # 3. Place first asset
            logger.info(f"Placing asset: {assets[0].name}")
            place_code = "import bpy\nfor obj in bpy.context.selected_objects:\n    obj.location = (0.0, 0.0, 0.0)\n"
            await self.blender.blender.execute_code(PythonCode(place_code))

            # 4. Setup environment (default HDRI for now)
            await self.blender.setup_environment(
                SetupEnvironmentRequestVO(
                    hdri_id=HdriId("default_studio"),
                )
            )

            return SuccessFlag(True)
        except BlenderMCPError as e:
            logger.error(f"Workflow failed: {e}")
            return SuccessFlag(False)
