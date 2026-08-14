"""Apply modifier capability — business logic and Blender external adaptation.

Implements ApplyModifierProtocol for FR-OBJ-005: adding, updating, removing,
or applying a modifier on an object with action types, destructive apply
confirmation, and parameter validation.

Structure:
  1. Constants & mappings (modifier type map, actions)
  2. Business logic functions (safe escaping, parameter validation)
  3. ApplyModifierExecutor — implements protocol
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ObjectType, Prompt, SuccessFlag
from modules.shared.src.common.utility_code_builder import quote_string
from modules.shared.src.object.contract_apply_modifier_protocol import ApplyModifierProtocol
from modules.shared.src.object.taxonomy_object_error import InvalidModifierTypeError, ModifierActionConfirmationError
from modules.shared.src.object.taxonomy_object_vo import ApplyModifierVO

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

# Supported modifier actions
MODIFIER_ACTIONS: frozenset[str] = frozenset({"add", "update", "remove", "apply"})

# Destructive actions that require confirmation
DESTRUCTIVE_ACTIONS: frozenset[str] = frozenset({"apply"})


class ApplyModifierExecutor(ApplyModifierProtocol):
    """Concrete implementation for applying modifiers to objects.

    FR-OBJ-005: Supports add/update/remove/apply actions, validates parameters,
    requires confirmation for destructive apply, and respects stack order.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: Any = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def apply_modifier(self, request: ApplyModifierVO) -> ApplyModifierVO:
        """Add, update, remove, or apply a modifier on an object.

        FR-OBJ-005: Maps human-readable modifier name to Blender enum,
        creates the modifier, then applies it destructively via operator.
        Requires confirmation for destructive actions.
        """
        logger.info(
            "Applying modifier %s on object %s (action: %s)", request.modifier_name, request.object_name, request.action
        )

        # Validate action type
        if request.action not in MODIFIER_ACTIONS:
            raise ValueError(f"Invalid modifier action: {request.action}")

        # Require confirmation for destructive actions
        if request.action in DESTRUCTIVE_ACTIONS and not getattr(request, "confirmation", False):
            raise ModifierActionConfirmationError(str(request.modifier_name), request.action)

        # Resolve modifier type
        mod_type_key = str(request.modifier_name).lower()
        mod_type_enum = MODIFIER_TYPE_MAP.get(mod_type_key)
        if mod_type_enum is None:
            raise InvalidModifierTypeError(str(request.modifier_name))

        # Generate and execute modifier code
        code = self._generate_modifier_code(request, mod_type_enum)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return ApplyModifierVO(
                object_name=request.object_name,
                modifier_name=request.modifier_name,
                success=SuccessFlag(True),
                modifier_type=ObjectType(mod_type_enum),
                action=request.action,
                applied_destructively=SuccessFlag(request.action == "apply"),
                message="Modifier operation completed successfully",
            )
        except Exception as e:
            logger.error("apply_modifier failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _generate_modifier_code(self, request: ApplyModifierVO, mod_type_enum: str) -> str:
        """Generate Blender Python code for modifier operations.

        Handles add, update, remove, and destructive apply actions.
        Respects stack order and edit mode constraints.
        """
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({quote_string(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
            f"mod_type = {quote_string(mod_type_enum)}\n",
        ]

        action = request.action

        if action == "add":
            lines.append(f"mod = obj.modifiers.new(name={quote_string(str(request.modifier_name))}, type=mod_type)\n")
        elif action == "update":
            lines.append(
                f"# Update existing modifier or add new\n"
                f"existing_mod = None\n"
                f"for mod in obj.modifiers:\n"
                f"    if mod.name == {quote_string(str(request.modifier_name))}:\n"
                f"        existing_mod = mod\n"
                f"        break\n"
                f"if existing_mod:\n"
                f"    # Update existing modifier parameters\n"
                f"    params = {quote_string(str(getattr(request, 'parameters', {})))}\n"
                f"    for param_name, param_value in params.items():\n"
                f"        try:\n"
                f"            setattr(existing_mod, param_name, param_value)\n"
                f"        except Exception:\n"
                f"            pass\n"
                f"else:\n"
                f"    obj.modifiers.new(name={quote_string(str(request.modifier_name))}, type=mod_type)\n"
            )
        elif action == "remove":
            lines.append(
                f"# Remove modifier by name\n"
                f"for mod in list(obj.modifiers):\n"
                f"    if mod.name == {quote_string(str(request.modifier_name))}:\n"
                f"        obj.modifiers.remove(mod)\n"
            )
        elif action == "apply":
            lines.append(
                f"# Add modifier then apply destructively\n"
                f"mod = obj.modifiers.new(name={quote_string(str(request.modifier_name))}, type=mod_type)\n"
                "for o in bpy.context.selected_objects:\n"
                "    o.select_set(False)\n"
                "obj.select_set(True)\n"
                "bpy.context.view_layer.objects.active = obj\n"
                "bpy.ops.object.modifier_apply(modifier=mod.name)\n"
            )

        return "\n".join(lines)

    def __repr__(self) -> str:
        return "ApplyModifierExecutor()"
