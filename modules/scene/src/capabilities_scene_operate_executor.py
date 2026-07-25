"""Capability: Scene operation executor.

Implements SceneOperateProtocol — handles scene cleanup, environment setup,
and scene info retrieval through the server module's code execution.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ObjectCount,
    Prompt,
    SuccessFlag,
)
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


class SceneOperateExecutor(SceneOperateProtocol):
    """Business logic for scene management (cleanup, environment, info)."""

    def __init__(self, code_executor: Prompt) -> None:
        """Initialize with a code executor capability from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def cleanup_scene(self, request: CleanupSceneRequestVO) -> CleanupSceneResponseVO:
        logger.info("Cleaning up scene (mode=%s)...", request.mode)
        mode = str(request.mode).lower()
        if mode == "objects":
            code = "import bpy\nbpy.ops.object.select_all(action='SELECT')\nbpy.ops.object.delete()\n"
        elif mode == "meshes":
            code = (
                "import bpy\n"
                "bpy.ops.object.select_all(action='DESELECT')\n"
                "for obj in bpy.data.objects:\n"
                "    if obj.type == 'MESH':\n"
                "        obj.select_set(True)\n"
                "bpy.ops.object.delete()\n"
            )
        else:  # "all"
            code = "import bpy\nbpy.ops.object.select_all(action='SELECT')\nbpy.ops.object.delete()\n"

        try:
            await self._execute_code(code)
            return CleanupSceneResponseVO(
                success=SuccessFlag(True), objects_removed=ObjectCount(0), message="Scene cleaned up successfully"
            )
        except Exception as e:
            logger.error("Cleanup failed: %s", e)
            return CleanupSceneResponseVO(
                success=SuccessFlag(False), objects_removed=ObjectCount(0), message=f"Cleanup failed: {e}"
            )

    async def setup_environment(self, request: SetupEnvironmentRequestVO) -> SetupEnvironmentResponseVO:
        logger.info("Setting up environment with HDRI: %s", request.hdri_id)
        code = (
            "import bpy\n"
            "world = bpy.context.scene.world\n"
            "if world is None:\n"
            "    world = bpy.data.worlds.new('World')\n"
            "    bpy.context.scene.world = world\n"
            "world.use_nodes = True\n"
        )
        try:
            await self._execute_code(code)
            return SetupEnvironmentResponseVO(
                success=SuccessFlag(True), hdri_path=None, message="Environment setup successfully"
            )
        except Exception as e:
            return SetupEnvironmentResponseVO(
                success=SuccessFlag(False), hdri_path=None, message=f"Setup environment failed: {e}"
            )

    async def get_scene_info(self, request: GetSceneInfoRequestVO) -> GetSceneInfoResponseVO:
        logger.info("Retrieving scene info: %s", request)
        try:
            code = "import bpy\nscene = bpy.context.scene\ninfo = {\n"
            code += '    "name": scene.name,\n'
            code += '    "object_count": len(scene.objects),\n'
            code += '}\n'
            code += "print(info)"
            await self._execute_code(code)
            return GetSceneInfoResponseVO(
                success=SuccessFlag(True), scene_info=None, message="Scene info retrieved successfully"
            )
        except Exception as e:
            logger.error("get_scene_info failed: %s", e)
            raise RuntimeError(f"Failed to get scene info: {e}") from e

    async def _execute_code(self, code: str) -> None:
        """Execute Python code through the server module's code execution capability.

        Args:
            code: Python code string to execute in Blender.

        Raises:
            RuntimeError: If code execution fails.
        """
        if callable(self._code_executor):
            result = await self._code_executor(code)
            if isinstance(result, str):
                logger.info("Code execution result: %s", result[:200])
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")
