"""Set material capability — business logic and Blender external adaptation.

Implements SetMaterialProtocol for FR-OBJ-004: assigning or creating a
material on an object with property validation, reuse policy, and slot creation.

Structure:
  1. Constants & mappings (material properties)
  2. Business logic functions (safe escaping, property validation)
  3. SetMaterialExecutor — implements protocol
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import Prompt, SuccessFlag
from modules.shared.src.object.contract_set_material_protocol import SetMaterialProtocol
from modules.shared.src.object.taxonomy_object_vo import SetMaterialVO

logger = logging.getLogger("BlenderMCPServer")


class SetMaterialExecutor(SetMaterialProtocol):
    """Concrete implementation for assigning materials to objects.

    FR-OBJ-004: Validates object supports materials, creates material if needed,
    validates property ranges, handles slot creation, and respects reuse policy.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: Any = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def set_material(self, request: SetMaterialVO) -> SetMaterialVO:
        """Assign or create a material on an object.

        FR-OBJ-004: Creates material if it doesn't exist; assigns to first slot
        or specified slot index. Validates object is a mesh type and PBR properties.
        """
        logger.info("Setting material %s on object %s", request.material_name, request.object_name)

        # Validate PBR properties if provided (FR-OBJ-004)
        base_color = getattr(request, "base_color", None)
        metallic = getattr(request, "metallic", None)
        roughness = getattr(request, "roughness", None)
        alpha = getattr(request, "alpha", None)

        if base_color is not None:
            for i, val in enumerate(base_color):
                if not isinstance(val, (int, float)) or val < 0 or val > 1:
                    raise ValueError(f"Base color component {i} must be in range [0, 1], got {val}")
        if metallic is not None and (not isinstance(metallic, (int, float)) or metallic < 0 or metallic > 1):
            raise ValueError(f"Metallic must be in range [0, 1], got {metallic}")
        if roughness is not None and (not isinstance(roughness, (int, float)) or roughness < 0 or roughness > 1):
            raise ValueError(f"Roughness must be in range [0, 1], got {roughness}")
        if alpha is not None and (not isinstance(alpha, (int, float)) or alpha < 0 or alpha > 1):
            raise ValueError(f"Alpha must be in range [0, 1], got {alpha}")

        # Generate and execute material assignment code
        code = self._generate_material_code(request)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return SetMaterialVO(
                object_name=request.object_name,
                material_name=request.material_name,
                success=SuccessFlag(True),
                message="Material set successfully",
            )
        except Exception as e:
            logger.error("set_material failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _generate_material_code(self, request: SetMaterialVO) -> str:
        """Generate Blender Python code for material assignment.

        Creates material if needed, validates object type, handles slot creation
        with optional index selection (FR-OBJ-004).
        """
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({SetMaterialExecutor._safe_str(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
            'if obj.type != "MESH":\n    raise ValueError(f"Object {obj.name!r} is not a mesh; cannot set material.")',
            f"mat = bpy.data.materials.get({SetMaterialExecutor._safe_str(str(request.material_name))})",
            "if not mat:\n"
            f'    mat = bpy.data.materials.new(name={SetMaterialExecutor._safe_str(str(request.material_name))})',
        ]

        # Handle slot creation/assignment with optional index (FR-OBJ-004)
        slot_index = getattr(request, "slot_index", None)
        if slot_index is not None:
            lines.append(
                f"# Assign material to specific slot index\n"
                f"while len(obj.data.materials) <= {slot_index}:\n"
                f'    obj.data.materials.append(bpy.data.materials.new(name="temp"))\n'
                f"obj.data.materials[{slot_index}] = mat\n"
            )
        else:
            lines.append(
                "if len(obj.data.materials) == 0:\n"
                "    obj.data.materials.append(mat)\n"
                "else:\n"
                "    obj.data.materials[0] = mat\n"
            )

        return "\n".join(lines)

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    def __repr__(self) -> str:
        return "SetMaterialExecutor()"
