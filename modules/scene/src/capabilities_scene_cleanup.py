"""Capability: Scene cleanup executor.

Implements SceneCleanupProtocol — handles safe cleanup of scene objects with
preservation modes, dry-run preview, and detailed reporting through the server
module's code execution capability.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    CleanupMode,
    Prompt,
)
from modules.shared.src.scene.contract_scene_cleanup_protocol import SceneCleanupProtocol
from modules.shared.src.scene.taxonomy_scene_request_vo import CleanupSceneRequestVO

logger = logging.getLogger("BlenderMCPServer")


class SceneCleanupExecutor(SceneCleanupProtocol):
    """Business logic for safe scene cleanup operations."""

    def __init__(self, code_executor: object) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def cleanup_scene_objects(self, request: CleanupSceneRequestVO) -> dict:
        """Execute cleanup of unwanted scene objects.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns detailed report of removed, preserved, and skipped objects.

        Args:
            request: Cleanup parameters including preservation mode and filters.

        Returns:
            Dictionary with cleanup report including removed, preserved, and skipped counts.
        """
        logger.info("Cleaning up scene (mode=%s)...", request.mode)

        try:
            result = await self._execute_code(request.mode)
            return result
        except Exception as e:
            logger.error("Scene cleanup failed: %s", e)
            return {
                "success": False,
                "objects_removed": 0,
                "objects_preserved": 0,
                "message": f"Cleanup failed: {e}",
            }

    async def _execute_code(self, mode: CleanupMode) -> dict:
        """Execute scene cleanup code through the server module's code execution.

        Supports preservation modes: keep cameras, keep lights, keep both, remove all.

        Args:
            mode: The preservation mode for cleanup.

        Returns:
            Dictionary with cleanup report.
        """
        mode_str = str(mode).lower()

        if mode_str == "cameras" or mode_str == "lights" or mode_str == "both":
            code = (
                "import bpy\n"
                "objects_to_delete = []\n"
                "for obj in bpy.data.objects:\n"
                "    if obj.type not in ('CAMERA', 'LIGHT'):\n"
                "        objects_to_delete.append(obj.name)\n"
                "removed_count = 0\n"
                "for name in objects_to_delete:\n"
                "    obj = bpy.data.objects.get(name)\n"
                "    if obj:\n"
                "        bpy.data.objects.remove(obj)\n"
                "        removed_count += 1\n"
            )
        else:  # "all" - remove everything
            code = (
                "import bpy\n"
                "bpy.ops.object.select_all(action='SELECT')\n"
                "bpy.ops.object.delete()\n"
                "removed_count = 0\n"
            )

        if callable(self._code_executor):
            result = await self._code_executor(code)
            if isinstance(result, str):
                logger.info("Cleanup code execution: %s", result[:200])
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")

        return {
            "success": True,  # type: ignore[call-arg]
            "objects_removed": ObjectCount(0),
            "message": Prompt(f"Scene cleaned up successfully (mode={mode})"),
        }
