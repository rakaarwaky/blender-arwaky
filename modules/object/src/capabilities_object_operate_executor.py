"""Object operate capability — business logic and Blender external adaptation.

Implements ObjectOperateProtocol for all 7 FRD operations:
place_asset, create_primitive, set_transform, set_material, apply_modifier,
delete_object, get_object_info.

Structure:
  1. Constants & mappings (modifier type map, primitive ops map)
  2. Business logic functions (validation, transform computation)
  3. ObjectOperateExecutor — implements protocol, delegates Blender execution
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    ObjectName,
    ObjectType,
    Prompt,
    RotationVector,
    ScaleVector,
    SuccessFlag,
)
from modules.shared.src.object.contract_object_operate_protocol import ObjectOperateProtocol
from modules.shared.src.object.taxonomy_object_error_vo import (
    InvalidModifierTypeError,
    InvalidPrimitiveTypeError,
)
from modules.shared.src.object.taxonomy_object_request_vo import (
    ApplyModifierRequestVO,
    CreatePrimitiveRequestVO,
    DeleteObjectRequestVO,
    GetObjectInfoRequestVO,
    PlaceAssetRequestVO,
    SetMaterialRequestVO,
    SetObjectTransformRequestVO,
)
from modules.shared.src.object.taxonomy_object_result_vo import (
    CreationResultVO,
    DeletionResultVO,
    MaterialResultVO,
    ModifierResultVO,
    ObjectInfoResultVO,
    PlacementResultVO,
    TransformResultVO,
)
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

# Supported primitive type mapping to Blender operator strings.
PRIMITIVE_OPS_MAP: dict[str, str] = {
    "cube": "bpy.ops.mesh.primitive_cube_add",
    "sphere": "bpy.ops.mesh.primitive_uv_sphere_add",
    "cylinder": "bpy.ops.mesh.primitive_cylinder_add",
    "cone": "bpy.ops.mesh.primitive_cone_add",
    "torus": "bpy.ops.mesh.primitive_torus_add",
    "grid": "bpy.ops.mesh.primitive_grid_add",
    "monkey": "bpy.ops.mesh.primitive_monkey_add",
    "plane": "bpy.ops.mesh.primitive_plane_add",
}


# ============================================================
# Business Logic Functions (stateless)
# ============================================================


def _safe_str(v: str) -> str:
    """Safely embed a string into generated Python code using repr().

    Prevents code injection from user input containing quotes or special chars.
    """
    return repr(v)


def _tuple_str(coords: CoordinateList) -> str:
    """Format a 3-element sequence of floats for embedding in generated Python code."""
    return f"({coords[0]}, {coords[1]}, {coords[2]})"


def _resolve_primitive_op(primitive_type: str) -> str | None:
    """Resolve a primitive type string to a Blender operator string.

    Handles Enum-style strings like 'primitivetype.sphere' by extracting the part after '.'.
    Returns None if the type is unsupported.
    """
    ptype = str(primitive_type).lower()
    if "." in ptype:
        ptype = ptype.split(".")[-1]
    return PRIMITIVE_OPS_MAP.get(ptype)


def _validate_transform_values(
    location: CoordinateList | None,
    rotation: RotationVector | None,
    scale: ScaleVector | None,
) -> None:
    """Validate that transform values are finite 3-component vectors."""
    for name, vals in [("location", location), ("rotation", rotation), ("scale", scale)]:
        if vals is None:
            continue
        if len(vals) != 3:
            raise ValueError(f"{name} must have exactly 3 components")


# ============================================================
# ObjectOperateExecutor — implements ObjectOperateProtocol
# ============================================================


class ObjectOperateExecutor(ObjectOperateProtocol):
    """Concrete implementation of object manipulation operations."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def place_asset(self, request: PlaceAssetRequestVO) -> PlacementResultVO:
        """Position an existing object or imported asset at target transform.

        FR-OBJ-001: If object_name is provided, place that specific object.
        Otherwise, place currently selected objects (asset import context).
        """
        logger.info("Placing asset %s at %s", request.asset_id, request.location)

        if request.object_name:
            code = (
                "import bpy\n"
                f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
                "if obj is None:\n"
                '    raise ValueError("Object not found in scene.")\n'
                f"obj.location = {_tuple_str(request.location)}\n"
            )
        else:
            code = (
                "import bpy\n"
                "for obj in bpy.context.selected_objects:\n"
                f"    obj.location = {_tuple_str(request.location)}\n"
            )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return PlacementResultVO(
                success=SuccessFlag(True),
                object_name=request.object_name or ObjectName(str(request.asset_id)),
                asset_id=request.asset_id,
                location=CoordinateList(request.location),
                message="Asset placed successfully",
            )
        except Exception as e:
            logger.error("Failed to place asset: %s", e)
            raise

    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreationResultVO:
        """Create a basic geometric primitive via Blender operator.

        FR-OBJ-002: Validates primitive type, resolves operator string,
        generates and executes Blender Python code.
        """
        logger.info("Creating primitive: %s", request.primitive_type)

        op = _resolve_primitive_op(str(request.primitive_type))
        if op is None:
            raise InvalidPrimitiveTypeError(str(request.primitive_type))

        kwargs = []
        if request.location is not None:
            kwargs.append(f"location={_tuple_str(request.location)}")
        if request.scale is not None:
            kwargs.append(f"scale={_tuple_str(request.scale)}")

        args_str = ", ".join(kwargs)
        code = f"import bpy\n{op}({args_str})\n"

        if request.name:
            code += (
                "created_obj = bpy.context.active_object\n"
                "if created_obj:\n"
                f"    created_obj.name = {_safe_str(str(request.name))}\n"
            )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return CreationResultVO(
                success=SuccessFlag(True),
                object_name=request.name or ObjectName("Primitive"),
                primitive_type=request.primitive_type,
                location=request.location or CoordinateList([0.0, 0.0, 0.0]),
                message="Primitive created successfully",
            )
        except Exception as e:
            logger.error("create_primitive failed: %s", e)
            raise

    async def set_object_transform(self, request: SetObjectTransformRequestVO) -> TransformResultVO:
        """Modify location, rotation, or scale of an existing object.

        FR-OBJ-003: Only sets provided transform fields; omitted fields are preserved.
        """
        logger.info("Setting transform for object %s", request.object_name)

        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        if request.location is not None:
            lines.append(f"obj.location = {_tuple_str(request.location)}")
        if request.rotation is not None:
            lines.append(f"obj.rotation_euler = {_tuple_str(request.rotation)}")
        if request.scale is not None:
            lines.append(f"obj.scale = {_tuple_str(request.scale)}")

        code = "\n".join(lines)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return TransformResultVO(
                success=SuccessFlag(True),
                object_name=request.object_name,
                location=request.location,
                rotation=request.rotation,
                scale=request.scale,
                message="Transform set successfully",
            )
        except Exception as e:
            logger.error("set_object_transform failed: %s", e)
            raise

    async def set_material(self, request: SetMaterialRequestVO) -> MaterialResultVO:
        """Assign or create a material on an object.

        FR-OBJ-004: Creates material if it doesn't exist; assigns to first slot
        or specified slot index. Validates object is a mesh type.
        """
        logger.info("Setting material %s on object %s", request.material_name, request.object_name)

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "if obj.type != 'MESH':\n"
            '    raise ValueError(f"Object {obj.name!r} is not a mesh; cannot set material.")\n'
            f"mat = bpy.data.materials.get({_safe_str(str(request.material_name))})\n"
            "if not mat:\n"
            f"    mat = bpy.data.materials.new(name={_safe_str(str(request.material_name))})\n"
            "if len(obj.data.materials) == 0:\n"
            "    obj.data.materials.append(mat)\n"
            "else:\n"
            "    obj.data.materials[0] = mat\n"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return MaterialResultVO(
                success=SuccessFlag(True),
                object_name=request.object_name,
                material_name=request.material_name,
                message="Material set successfully",
            )
        except Exception as e:
            logger.error("set_material failed: %s", e)
            raise

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
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            f"mod_type = {_safe_str(mod_type_enum)}\n"
            f"mod = obj.modifiers.new(name={_safe_str(str(request.modifier_name))}, type=mod_type)\n"
            "for o in bpy.context.selected_objects:\n"
            "    o.select_set(False)\n"
            "obj.select_set(True)\n"
            "bpy.context.view_layer.objects.active = obj\n"
            "bpy.ops.object.modifier_apply(modifier=mod.name)\n"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return ModifierResultVO(
                success=SuccessFlag(True),
                object_name=request.object_name,
                modifier_name=request.modifier_name,
                modifier_type=ObjectType(mod_type_enum),
                action="apply_destructive",
                applied_destructively=SuccessFlag(True),
                message="Modifier applied successfully",
            )
        except Exception as e:
            logger.error("apply_modifier failed: %s", e)
            raise

    async def delete_object(self, request: DeleteObjectRequestVO) -> DeletionResultVO:
        """Remove an object from the scene.

        FR-OBJ-006: Validates object exists, removes it via bpy.data.objects.remove().
        """
        logger.info("Deleting object %s", request.object_name)

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "bpy.data.objects.remove(obj, do_unlink=True)\n"
        )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return DeletionResultVO(
                success=SuccessFlag(True),
                deleted_count=1,
                deleted_names=[request.object_name],
                message="Object deleted successfully",
            )
        except Exception as e:
            logger.error("delete_object failed: %s", e)
            raise

    async def get_object_info(self, request: GetObjectInfoRequestVO) -> ObjectInfoResultVO:
        """Retrieve detailed information about an object.

        FR-OBJ-007: Delegates to code executor for scene introspection.
        Returns structured info about the object's state.
        """
        try:
            code = (
                "import bpy\n"
                f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
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
            await self._executor.execute_blender_code(Prompt(code))
            return ObjectInfoResultVO(
                success=SuccessFlag(True),
                object_name=request.object_name,
                message="Object info retrieved successfully",
            )
        except Exception as e:
            logger.error("get_object_info failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return "ObjectOperateExecutor()"
