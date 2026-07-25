"""Delete object capability — business logic and Blender external adaptation.

Implements DeleteObjectProtocol for FR-OBJ-006: removing an object from
the scene.

Structure:
  1. Constants & mappings
  2. Business logic functions (safe escaping)
  3. DeleteObjectExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import ObjectCount, ObjectName, Prompt
from modules.shared.src.object.contract_delete_object_protocol import DeleteObjectProtocol
from modules.shared.src.object.taxonomy_object_request_vo import DeleteObjectRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import DeletionResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")


class DeleteObjectExecutor(DeleteObjectProtocol):
    """Concrete implementation for deleting objects from the scene."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def delete_object(self, request: DeleteObjectRequestVO) -> DeletionResultVO:
        """Remove an object from the scene.

        FR-OBJ-006: Validates object exists, removes it via bpy.data.objects.remove().
        """
        logger.info("Deleting object %s", request.object_name)

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({DeleteObjectExecutor._safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "bpy.data.objects.remove(obj, do_unlink=True)\n"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return DeletionResultVO(
                success=True,  # type: ignore[arg-type]
                deleted_count=1,
                deleted_names=[request.object_name],
                message="Object deleted successfully",
            )
        except Exception as e:
            logger.error("delete_object failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    def __repr__(self) -> str:
        return "DeleteObjectExecutor()"
