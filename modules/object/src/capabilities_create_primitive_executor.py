"""Create primitive capability — business logic and Blender external adaptation.

Implements CreatePrimitiveProtocol for FR-OBJ-002: creating basic geometric
primitives via Blender operators.

Structure:
  1. Constants & mappings (primitive ops map)
  2. Business logic functions (type resolution, safe escaping)
  3. CreatePrimitiveExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    ObjectName,
    ObjectType,
    Prompt,
    ScaleVector,
)
from modules.shared.src.object.contract_create_primitive_protocol import CreatePrimitiveProtocol
from modules.shared.src.object.taxonomy_object_error_vo import InvalidPrimitiveTypeError
from modules.shared.src.object.taxonomy_object_request_vo import CreatePrimitiveRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import CreationResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")

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


class CreatePrimitiveExecutor(CreatePrimitiveProtocol):
    """Concrete implementation for creating geometric primitives."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreationResultVO:
        """Create a basic geometric primitive via Blender operator.

        FR-OBJ-002: Validates primitive type, resolves operator string,
        generates and executes Blender Python code.
        """
        logger.info("Creating primitive: %s", request.primitive_type)

        op = CreatePrimitiveExecutor._resolve_primitive_op(str(request.primitive_type))
        if op is None:
            raise InvalidPrimitiveTypeError(str(request.primitive_type))

        kwargs = []
        if request.location is not None:
            kwargs.append(f"location={CreatePrimitiveExecutor._tuple_str(request.location)}")
        if request.scale is not None:
            kwargs.append(f"scale={CreatePrimitiveExecutor._tuple_str(request.scale)}")

        args_str = ", ".join(kwargs)
        code = f"import bpy\n{op}({args_str})\n"

        if request.name:
            code += (
                "created_obj = bpy.context.active_object\n"
                "if created_obj:\n"
                f"    created_obj.name = {CreatePrimitiveExecutor._safe_str(str(request.name))}\n"
            )

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return CreationResultVO(
                success=True,  # type: ignore[arg-type]
                object_name=request.name or ObjectName("Primitive"),
                primitive_type=request.primitive_type,
                location=request.location or CoordinateList([0.0, 0.0, 0.0]),
                message="Primitive created successfully",
            )
        except Exception as e:
            logger.error("create_primitive failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @staticmethod
    def _safe_str(v: str) -> str:
        """Safely embed a string into generated Python code using repr()."""
        return repr(v)

    @staticmethod
    def _tuple_str(coords: CoordinateList) -> str:
        """Format a 3-element sequence of floats for embedding in generated Python code."""
        return f"({coords[0]}, {coords[1]}, {coords[2]})"

    @staticmethod
    def _resolve_primitive_op(primitive_type: str) -> str | None:
        """Resolve a primitive type string to a Blender operator string.

        Handles Enum-style strings like 'primitivetype.sphere' by extracting the part after '.'.
        Returns None if the type is unsupported.
        """
        ptype = str(primitive_type).lower()
        if "." in ptype:
            ptype = ptype.split(".")[-1]
        return PRIMITIVE_OPS_MAP.get(ptype)

    def __repr__(self) -> str:
        return "CreatePrimitiveExecutor()"
