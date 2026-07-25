"""Handler: Blender object manipulation operations."""

import logging

from modules.shared.src import BlenderPort, ObjectOperateProtocol
from modules.shared.src import (
    ApplyModifierRequestVO,
    ApplyModifierResponseVO,
    BlenderMCPError,
    CoordinateList,
    CreatePrimitiveRequestVO,
    CreatePrimitiveResponseVO,
    DeleteObjectRequestVO,
    DeleteObjectResponseVO,
    ErrorMessage,
    GetObjectInfoRequestVO,
    GetObjectInfoResponseVO,
    ObjectName,
    PlaceAssetRequestVO,
    PlaceAssetResponseVO,
    PythonCode,
    SetMaterialRequestVO,
    SetMaterialResponseVO,
    SetObjectTransformRequestVO,
    SetObjectTransformResponseVO,
    SuccessFlag,
)

logger = logging.getLogger("BlenderMCPServer")

# Mapping from human-readable modifier names to Blender's internal enum strings.
# This prevents the bug where .upper() produces invalid enums like "SUBDIVISION SURFACE".
MODIFIER_MAP: dict[str, str] = {
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


def _safe_str(v: str) -> str:
    """Safely embed a string into generated Python code using repr().

    This prevents code injection attacks where user input containing quotes
    or special characters could be executed as Python code.
    """
    return repr(v)


def _tuple_str(coords: CoordinateList) -> str:
    """Format a 3-element sequence of floats for embedding in generated Python code."""
    return f"({coords[0]}, {coords[1]}, {coords[2]})"


class ObjectOperateExecutor(ObjectOperateProtocol):
    """Business logic for object manipulation (transform, material, etc.)."""

    def __init__(self, blender_port: BlenderPort):
        self.blender = blender_port

    async def place_asset(self, request: PlaceAssetRequestVO) -> PlaceAssetResponseVO:
        logger.info(f"Placing asset {request.asset_id} at {request.location}")
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
            await self.blender.execute_code(PythonCode(code))
            return PlaceAssetResponseVO(
                success=SuccessFlag(True),
                object_name=request.object_name or ObjectName(str(request.asset_id)),
                asset_id=request.asset_id,
                location=CoordinateList(request.location),
                message="Asset placed successfully",
            )
        except Exception as e:
            logger.error(f"Failed to place asset: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to place asset: {e}")) from e

    async def get_object_info(self, request: GetObjectInfoRequestVO) -> GetObjectInfoResponseVO:
        try:
            obj = await self.blender.get_object_info(request.object_name)
            return GetObjectInfoResponseVO(
                success=SuccessFlag(True), object_info=obj, message="Object info retrieved successfully"
            )
        except Exception as e:
            logger.error(f"get_object_info failed: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to get object info: {e}")) from e

    async def set_object_transform(self, request: SetObjectTransformRequestVO) -> SetObjectTransformResponseVO:
        logger.info(f"Setting transform for object {request.object_name}")
        lines = ["import bpy", f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})", "if obj is None:"]
        lines.append('    raise ValueError("Object not found in scene.")')
        if request.location is not None:
            lines.append(f"obj.location = {_tuple_str(request.location)}")
        if request.rotation is not None:
            lines.append(f"obj.rotation_euler = {_tuple_str(request.rotation)}")
        if request.scale is not None:
            lines.append(f"obj.scale = {_tuple_str(request.scale)}")
        code = "\n".join(lines)
        try:
            await self.blender.execute_code(PythonCode(code))
            return SetObjectTransformResponseVO(
                success=SuccessFlag(True), object_name=request.object_name, message="Transform set successfully"
            )
        except Exception as e:
            logger.error(f"set_object_transform failed: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to set transform: {e}")) from e

    async def delete_object(self, request: DeleteObjectRequestVO) -> DeleteObjectResponseVO:
        logger.info(f"Deleting object {request.object_name}")
        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "bpy.data.objects.remove(obj, do_unlink=True)\n"
        )
        try:
            await self.blender.execute_code(PythonCode(code))
            return DeleteObjectResponseVO(
                success=SuccessFlag(True), object_name=request.object_name, message="Object deleted successfully"
            )
        except Exception as e:
            logger.error(f"delete_object failed: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to delete object: {e}")) from e

    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreatePrimitiveResponseVO:
        logger.info(f"Creating primitive: {request.primitive_type}")
        ptype = str(request.primitive_type).lower()

        ops_map = {
            "cube": "bpy.ops.mesh.primitive_cube_add",
            "sphere": "bpy.ops.mesh.primitive_uv_sphere_add",
            "cylinder": "bpy.ops.mesh.primitive_cylinder_add",
            "cone": "bpy.ops.mesh.primitive_cone_add",
            "torus": "bpy.ops.mesh.primitive_torus_add",
            "grid": "bpy.ops.mesh.primitive_grid_add",
            "monkey": "bpy.ops.mesh.primitive_monkey_add",
            "plane": "bpy.ops.mesh.primitive_plane_add",
        }
        # Handle Enum-style strings like "primitivetype.sphere" by extracting the part after '.'
        if "." in ptype:
            ptype = ptype.split(".")[-1]

        try:
            op = ops_map.get(ptype)
            if op is None:
                raise ValueError(f"Unsupported primitive type: {request.primitive_type}")

            kwargs = []
            if request.location is not None:
                kwargs.append(f"location={_tuple_str(request.location)}")
            if request.scale is not None:
                kwargs.append(f"scale={_tuple_str(request.scale)}")

            args_str = ", ".join(kwargs)

            code = f"import bpy\n{op}({args_str})\n"
            if request.name:
                code += (
                    f"created_obj = bpy.context.active_object\n"
                    f"if created_obj:\n"
                    f"    created_obj.name = {_safe_str(str(request.name))}\n"
                )

            await self.blender.execute_code(PythonCode(code))
            return CreatePrimitiveResponseVO(
                success=SuccessFlag(True),
                object_name=request.name or ObjectName("Primitive"),
                primitive_type=request.primitive_type,
                message="Primitive created successfully",
            )
        except Exception as e:
            logger.error(f"create_primitive failed: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to create primitive: {e}")) from e

    async def set_material(self, request: SetMaterialRequestVO) -> SetMaterialResponseVO:
        logger.info(f"Setting material {request.material_name} on object {request.object_name}")
        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            "if obj.type != 'MESH':\n"
            '    raise ValueError(f"Object {obj.name!r} is not a mesh; cannot set material.")\n'
            f"mat = bpy.data.materials.get({_safe_str(str(request.material_name))})\n"
            f"if not mat:\n"
            f"    mat = bpy.data.materials.new(name={_safe_str(str(request.material_name))})\n"
            "if len(obj.data.materials) == 0:\n"
            "    obj.data.materials.append(mat)\n"
            "else:\n"
            "    obj.data.materials[0] = mat\n"
        )
        try:
            await self.blender.execute_code(PythonCode(code))
            return SetMaterialResponseVO(
                success=SuccessFlag(True),
                object_name=request.object_name,
                material_name=request.material_name,
                message="Material set successfully",
            )
        except Exception as e:
            logger.error(f"set_material failed: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to set material: {e}")) from e

    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ApplyModifierResponseVO:
        logger.info(f"Applying modifier {request.modifier_name} on object {request.object_name}")
        # Map human-readable names to Blender's internal enum strings.
        mod_type_key = str(request.modifier_name).lower()
        mod_type_enum = MODIFIER_MAP.get(mod_type_key)
        if mod_type_enum is None:
            raise ValueError(f"Unsupported modifier type: {request.modifier_name}")

        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get({_safe_str(str(request.object_name))})\n"
            "if obj is None:\n"
            '    raise ValueError("Object not found in scene.")\n'
            f"mod_type = {_safe_str(mod_type_enum)}\n"
            f"mod = obj.modifiers.new(name={_safe_str(str(request.modifier_name))}, type=mod_type)\n"
            # Deselect all objects, then select the target for modifier_apply operator.
            "for o in bpy.context.selected_objects:\n"
            "    o.select_set(False)\n"
            "obj.select_set(True)\n"
            "bpy.context.view_layer.objects.active = obj\n"
            "bpy.ops.object.modifier_apply(modifier=mod.name)\n"
        )
        try:
            await self.blender.execute_code(PythonCode(code))
            return ApplyModifierResponseVO(
                success=SuccessFlag(True),
                object_name=request.object_name,
                modifier_name=request.modifier_name,
                message="Modifier applied successfully",
            )
        except Exception as e:
            logger.error(f"apply_modifier failed: {e}")
            raise BlenderMCPError(ErrorMessage(f"Failed to apply modifier: {e}")) from e
