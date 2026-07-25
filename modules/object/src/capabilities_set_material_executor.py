"""Set material capability — business logic and Blender external adaptation.

Implements SetMaterialProtocol for FR-OBJ-004: assigning or creating a
material on an object.

Structure:
  1. Constants & mappings
  2. Business logic functions (safe escaping)
  3. SetMaterialExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import ObjectName, Prompt
from modules.shared.src.object.contract_set_material_protocol import SetMaterialProtocol
from modules.shared.src.object.taxonomy_object_request_vo import SetMaterialRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import MaterialResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")


class SetMaterialExecutor(SetMaterialProtocol):
    """Concrete implementation for assigning materials to objects."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def set_material(self, request: SetMaterialRequestVO) -> MaterialResultVO:
        """Assign or create a material on an object.

        FR-OBJ-004: Creates material if it doesn't exist; assigns to first slot
        or specified slot index. Validates object is a mesh type.
        """
        logger.info("Setting material %s on object %s", request.material_name, request.object_name)

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({SetMaterialExecutor._safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "if obj.type != 'MESH':\n"
            '    raise ValueError(f"Object {obj.name!r} is not a mesh; cannot set material.")\n'
            f"mat = bpy.data.materials.get({SetMaterialExecutor._safe_str(str(request.material_name))})\n"
            "if not mat:\n"
            f"    mat = bpy.data.materials.new(name={SetMaterialExecutor._safe_str(str(request.material_name))})\n"
            "if len(obj.data.materials) == 0:\n"
            "    obj.data.materials.append(mat)\n"
            "else:\n"
            "    obj.data.materials[0] = mat\n"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return MaterialResultVO(
                success=True,  # type: ignore[arg-type]
                object_name=request.object_name,
                material_name=request.material_name,
                message="Material set successfully",
            )
        except Exception as e:
            logger.error("set_material failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    def __repr__(self) -> str:
        return "SetMaterialExecutor()"
