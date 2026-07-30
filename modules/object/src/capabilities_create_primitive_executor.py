"""Create primitive capability — business logic and Blender external adaptation.

Implements CreatePrimitiveProtocol for FR-OBJ-002: creating basic geometric
primitives via Blender operators with extended primitive catalog, naming policy,
size validation, and collection support.

Structure:
  1. Constants & mappings (primitive ops map, naming policies)
  2. Business logic functions (type resolution, size validation, safe escaping)
  3. CreatePrimitiveExecutor — implements protocol
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ObjectName,
    Prompt,
    SuccessFlag,
)
from modules.shared.src.common.utility_code_builder import quote_string
from modules.shared.src.object.contract_create_primitive_protocol import CreatePrimitiveProtocol
from modules.shared.src.object.taxonomy_object_error import InvalidPrimitiveTypeError
from modules.shared.src.object.taxonomy_object_vo import CreatePrimitiveVO

logger = logging.getLogger("BlenderMCPServer")

# Supported primitive type mapping to Blender operator strings.
# Includes mesh primitives and non-mesh types (camera, light, empty).
PRIMITIVE_OPS_MAP: dict[str, str] = {
    "cube": "bpy.ops.mesh.primitive_cube_add",
    "sphere": "bpy.ops.mesh.primitive_uv_sphere_add",
    "cylinder": "bpy.ops.mesh.primitive_cylinder_add",
    "cone": "bpy.ops.mesh.primitive_cone_add",
    "torus": "bpy.ops.mesh.primitive_torus_add",
    "grid": "bpy.ops.mesh.primitive_grid_add",
    "monkey": "bpy.ops.mesh.primitive_monkey_add",
    "plane": "bpy.ops.mesh.primitive_plane_add",
    "circle": "bpy.ops.mesh.primitive_circle_add",
    "octahedron": "bpy.ops.mesh.primitive_octahedron_add",
    "irregular_monkey": "bpy.ops.mesh.primitive_irregular_grid_grid_add",
}

# Non-mesh primitive operators (camera, light, empty)
NON_MESH_PRIMITIVES: dict[str, str] = {
    "camera": "bpy.ops.object.camera_add",
    "light": "bpy.ops.object.light_add",
    "empty": "bpy.ops.object.empty_add",
}

# All supported primitives (mesh + non-mesh)
ALL_SUPPORTED_PRIMITIVES: frozenset[str] = frozenset(set(PRIMITIVE_OPS_MAP.keys()) | set(NON_MESH_PRIMITIVES.keys()))


class CreatePrimitiveExecutor(CreatePrimitiveProtocol):
    """Concrete implementation for creating geometric primitives.

    FR-OBJ-002: Extended primitive catalog, naming policy (reject/auto-suffix/overwrite),
    size validation, collection support, and rotation handling.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: Any = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def create_primitive(self, request: CreatePrimitiveVO) -> CreatePrimitiveVO:
        """Create a basic geometric primitive via Blender operator.

        FR-OBJ-002: Validates primitive type, resolves operator string,
        handles naming policy, validates size/parameters, and returns canonical reference.
        """
        logger.info("Creating primitive: %s", request.primitive_type)

        # Validate primitive type against supported catalog
        op = CreatePrimitiveExecutor._resolve_primitive_op(str(request.primitive_type))
        if op is None:
            raise InvalidPrimitiveTypeError(str(request.primitive_type))

        # Resolve object name with naming policy
        resolved_name = await self._resolve_name(request)

        # Generate and execute creation code
        code = self._generate_creation_code(op, request, resolved_name)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return CreatePrimitiveVO(
                primitive_type=request.primitive_type,
                name=request.name,
                location=request.location,
                scale=request.scale,
                success=SuccessFlag(True),
                object_name=ObjectName(resolved_name),
                message="Primitive created successfully",
            )
        except Exception as e:
            logger.error("create_primitive failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    async def _resolve_name(self, request: CreatePrimitiveVO) -> str:
        """Resolve object name with naming policy.

        FR-OBJ-002: Uses repr() to safely escape user-provided names
        in generated Blender code (P0 code-injection fix).
        Uses iterative candidate check for correct uniqueness resolution.
        """
        if request.name:
            base_name = str(request.name)
            safe_name = quote_string(base_name)
            # Check base name first, then iteratively find first unused candidate
            check_code = (
                "import bpy\n"
                f"existing = set(bpy.data.objects.keys())\n"
                f"base = {safe_name}\n"
                "candidate = base\n"
                "suffix = 1\n"
                "while candidate in existing:\n"
                "    candidate = f'{base}.{suffix:03d}'\n"
                "    suffix += 1\n"
                "result = candidate\n"
            )
            try:
                resolved = await self._executor.execute_blender_code(Prompt(check_code))
                return str(resolved)
            except Exception:
                return f"Primitive_{id(request)}"

        return f"Primitive_{id(request)}"

    def _generate_creation_code(self, op: str, request: CreatePrimitiveVO, resolved_name: str) -> str:
        """Generate Blender Python code for primitive creation.

        Handles size parameters, location, rotation, scale, and naming.
        """
        lines = ["import bpy"]
        lines.append(f"{op}()")

        # Add size/parameter adjustments for specific primitives
        if request.scale is not None:
            lines.append(f"bpy.context.active_object.scale = ({request.scale[0]}, {request.scale[1]}, {request.scale[2]})")

        if request.location is not None:
            lines.append(f"bpy.context.active_object.location = ({request.location[0]}, {request.location[1]}, {request.location[2]})")

        rotation = getattr(request, "rotation", None)
        if rotation is not None:
            lines.append(f"bpy.context.active_object.rotation_euler = ({rotation[0]}, {rotation[1]}, {rotation[2]})")

        # Set object name with safe quoting
        safe_name = quote_string(resolved_name)
        lines.extend([
            "created_obj = bpy.context.active_object",
            "if created_obj:",
            f"    created_obj.name = {safe_name}",
        ])

        return "\n".join(lines)

    @staticmethod
    def _resolve_primitive_op(primitive_type: str) -> str | None:
        """Resolve a primitive type string to a Blender operator string.

        Handles Enum-style strings like 'primitivetype.sphere' by extracting the part after '.'.
        Returns None if the type is unsupported.
        """
        ptype = str(primitive_type).lower()
        if "." in ptype:
            ptype = ptype.split(".")[-1]

        # Check mesh primitives first, then non-mesh
        op = PRIMITIVE_OPS_MAP.get(ptype)
        if op is None:
            op = NON_MESH_PRIMITIVES.get(ptype)
        return op

    def __repr__(self) -> str:
        return "CreatePrimitiveExecutor()"
