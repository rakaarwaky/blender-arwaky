"""Apply modifier capability — business logic and Blender external adaptation.

Implements ApplyModifierProtocol for FR-OBJ-005: adding, updating, removing,
or applying a modifier on an object destructively.

Structure:
  1. Constants & mappings (modifier type map)
  2. Business logic functions (safe escaping)
  3. ApplyModifierExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import ObjectName, ObjectType, Prompt
from modules.shared.src.object.contract_apply_modifier_protocol import ApplyModifierProtocol
from modules.shared.src.object.taxonomy_object_error_vo import InvalidModifierTypeError
from modules.shared.src.object.taxonomy_object_request_vo import ApplyModifierRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import ModifierResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")

# Mapping from human-readable modifier names to Blender's internal enum strings.
MODIFIER_TYPE_MAP: dict[str, str] = {
    "subsurf": "SUBSURF",
    "subdivision surface": "SUBSURF",
    "mirror": "MIRROR",
    "bevel": "BEVEL",
    "solidify": "SOLIDIFY",
    "array": "ARRAY",
    "displace": "DISPLACE",
    "curve": "CURVE",
    "deflect": "DEFLECT",
    "edge split": "EDGE_SPLIT",
    "extrude region": "EXTRUDE_REGION",
    "mesh deform": "MESH_DEFORM",
    "rigid body": "RIGID_BODY",
    "shrink wrap": "SHRINKWRAP",
    "smoke": "SMOKE",
    "soft body": "SOFT_BODY",
    "spring": "SPRING",
    "surface fdt": "SURFACE_FDT",
}


class ApplyModifierExecutor(ApplyModifierProtocol):
    """Concrete implementation for applying modifiers to objects."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ModifierResultVO:
        """Add and apply a modifier on an object destructively.

        FR-OBJ-005: Maps human-readable modifier name to Blender enum,
        creates the modifier, then applies it destructively via operator.
        """
        logger.info("Applying modifier %s on object %s", request.modifier_name, request.object_name)

        mod_type_key = str(request.modifier_name).lower()
        mod_type_enum = MODIFIER_TYPE_MAP.get(mod_type_key)
        if mod_type_enum is None:
            raise InvalidModifierTypeError(str(request.modifier_name))

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({ApplyModifierExecutor._safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            f"mod_type = {ApplyModifierExecutor._safe_str(mod_type_enum)}\n"
            f"mod = obj.modifiers.new(name={ApplyModifierExecutor._safe_str(str(request.modifier_name))}, type=mod_type)\n"
            "for o in bpy.context.selected_objects:\n"
            "    o.select_set(False)\n"
            "obj.select_set(True)\n"
            "bpy.context.view_layer.objects.active = obj\n"
            "bpy.ops.object.modifier_apply(modifier=mod.name)\n"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return ModifierResultVO(
                success=True,  # type: ignore[arg-type]
                object_name=request.object_name,
                modifier_name=request.modifier_name,
                modifier_type=ObjectType(mod_type_enum),
                action="apply_destructive",
                applied_destructively=True,  # type: ignore[arg-type]
                message="Modifier applied successfully",
            )
        except Exception as e:
            logger.error("apply_modifier failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    def __repr__(self) -> str:
        return "ApplyModifierExecutor()"
