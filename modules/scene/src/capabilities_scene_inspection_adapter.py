"""Capability: Scene inspection adapter.

Implements SceneInspectionPort — handles scene info, object info, and cleanup
through the server module's command dispatch and code execution capabilities.
"""

from __future__ import annotations

import json
import logging

from modules.shared.src.common.taxonomy_core_vo import ActionName, ObjectName, Prompt
from modules.shared.src.scene.contract_scene_inspection import SceneInspectionPort

logger = logging.getLogger("BlenderMCPServer")


class SceneInspectionAdapter(SceneInspectionPort):
    """Scene inspection functions via server command dispatch."""

    def __init__(self, command_sender: Prompt, code_executor: Prompt) -> None:
        """Initialize with server module capabilities.

        Args:
            command_sender: A callable that sends commands to Blender.
            code_executor: A callable that executes Python code in Blender.
        """
        self._command_sender = command_sender
        self._code_executor = code_executor

    async def get_scene_info(self) -> Prompt:
        try:
            result = self._command_sender(ActionName("get_scene_info"))
            return Prompt(json.dumps(result, indent=2))
        except Exception as e:
            logger.error("Error getting scene info from Blender: %s", e)
            return Prompt(f"Error getting scene info: {e}")

    async def get_object_info(self, object_name: ObjectName) -> Prompt:
        try:
            result = self._command_sender(ActionName("get_object_info"), {"name": object_name})
            return Prompt(json.dumps(result, indent=2))
        except Exception as e:
            logger.error("Error getting object info from Blender: %s", e)
            return Prompt(f"Error getting object info: {e}")

    async def cleanup_scene(self) -> Prompt:
        code = "import bpy\nbpy.ops.object.select_all(action='SELECT')\nbpy.ops.object.delete()\n"
        try:
            result = await self._code_executor(Prompt(code))
            return result
        except Exception as e:
            logger.error("Cleanup failed: %s", e)
            return Prompt(f"Error cleaning scene: {e}")
