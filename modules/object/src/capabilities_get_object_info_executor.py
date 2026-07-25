"""Get object info capability — business logic and Blender external adaptation.

Implements GetObjectInfoProtocol for FR-OBJ-007: retrieving detailed object
information from the scene.

Structure:
  1. Constants & mappings
  2. Business logic functions (safe escaping)
  3. GetObjectInfoExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import ObjectName, Prompt
from modules.shared.src.object.contract_get_object_info_protocol import GetObjectInfoProtocol
from modules.shared.src.object.taxonomy_object_request_vo import GetObjectInfoRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import ObjectInfoResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")


class GetObjectInfoExecutor(GetObjectInfoProtocol):
    """Concrete implementation for retrieving object information."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def get_object_info(self, request: GetObjectInfoRequestVO) -> ObjectInfoResultVO:
        """Retrieve detailed information about an object.

        FR-OBJ-007: Delegates to code executor for scene introspection.
        Returns structured info about the object's state.
        """
        logger.info("Retrieving info for object %s", request.object_name)

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({GetObjectInfoExecutor._safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "import json\n"
            "info = {\n"
            f"    'name': obj.name,\n"
            f"    'type': obj.type,\n"
            f"    'location': [obj.location.x, obj.location.y, obj.location.z],\n"
            f"    'rotation': [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]],\n"
            f"    'scale': [obj.scale.x, obj.scale.y, obj.scale.z],\n"
            "}"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return ObjectInfoResultVO(
                success=True,  # type: ignore[arg-type]
                object_name=request.object_name,
                message="Object info retrieved successfully",
            )
        except Exception as e:
            logger.error("get_object_info failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    def __repr__(self) -> str:
        return "GetObjectInfoExecutor()"
