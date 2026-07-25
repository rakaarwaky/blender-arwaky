"""Set transform capability — business logic and Blender external adaptation.

Implements SetObjectTransformProtocol for FR-OBJ-003: modifying location,
rotation, or scale of an existing object.

Structure:
  1. Constants & mappings
  2. Business logic functions (safe escaping, tuple formatting)
  3. SetTransformExecutor — implements protocol
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import CoordinateList, ObjectName, Prompt
from modules.shared.src.object.contract_set_transform_protocol import SetObjectTransformProtocol
from modules.shared.src.object.taxonomy_object_request_vo import SetObjectTransformRequestVO
from modules.shared.src.object.taxonomy_object_result_vo import TransformResultVO
from modules.shared.src.server.contract_code_execution_protocol import ICodeExecutionProtocol

logger = logging.getLogger("BlenderMCPServer")


class SetTransformExecutor(SetObjectTransformProtocol):
    """Concrete implementation for modifying object transforms."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def set_object_transform(
        self, request: SetObjectTransformRequestVO
    ) -> TransformResultVO:
        """Modify location, rotation, or scale of an existing object.

        FR-OBJ-003: Only sets provided transform fields; omitted fields are preserved.
        """
        logger.info("Setting transform for object %s", request.object_name)

        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({SetTransformExecutor._safe_str(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        if request.location is not None:
            lines.append(f"obj.location = {SetTransformExecutor._tuple_str(request.location)}")
        if request.rotation is not None:
            lines.append(f"obj.rotation_euler = {SetTransformExecutor._tuple_str(request.rotation)}")
        if request.scale is not None:
            lines.append(f"obj.scale = {SetTransformExecutor._tuple_str(request.scale)}")

        code = "\n".join(lines)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return TransformResultVO(
                success=True,  # type: ignore[arg-type]
                object_name=request.object_name,
                location=request.location,
                rotation=request.rotation,
                scale=request.scale,
                message="Transform set successfully",
            )
        except Exception as e:
            logger.error("set_object_transform failed: %s", e)
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

    def __repr__(self) -> str:
        return "SetTransformExecutor()"
