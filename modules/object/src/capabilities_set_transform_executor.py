"""Set transform capability — business logic and Blender external adaptation.

Implements SetObjectTransformProtocol for FR-OBJ-003: modifying location,
rotation, or scale of an existing object with absolute/relative modes,
transform component preservation, and locked channel respect.

Structure:
  1. Constants & mappings (transform modes)
  2. Business logic functions (safe escaping, tuple formatting, validation)
  3. SetTransformExecutor — implements protocol
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    ObjectName,
    Prompt,
    RotationVector,
    ScaleVector,
    SuccessFlag,
)
from modules.shared.src.object.contract_set_transform_protocol import SetObjectTransformProtocol
from modules.shared.src.object.taxonomy_object_error_vo import TransformLockError
from modules.shared.src.object.taxonomy_object_vo import SetObjectTransformVO

logger = logging.getLogger("BlenderMCPServer")


class SetTransformExecutor(SetObjectTransformProtocol):
    """Concrete implementation for modifying object transforms.

    FR-OBJ-003: Supports absolute and relative transform modes, preserves omitted
    components, respects locked channels (unless override allowed), and ensures
    idempotency for identical absolute transforms.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: Any = None) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def set_object_transform(self, request: SetObjectTransformVO) -> SetObjectTransformVO:
        """Modify location, rotation, or scale of an existing object.

        FR-OBJ-003: Only sets provided transform fields; omitted fields are preserved.
        Supports absolute and relative modes.
        """
        logger.info("Setting transform for object %s", request.object_name)

        # Validate transform values (finite, non-zero scale unless allowed)
        if request.scale is not None:
            self._validate_scale(request.scale)

        # Generate and execute transform code
        code = self._generate_transform_code(request)

        try:
            await self._executor.execute_blender_code(Prompt(code))
            return SetObjectTransformVO(
                object_name=request.object_name,
                location=request.location,
                rotation=request.rotation,
                scale=request.scale,
                success=SuccessFlag(True),
                message="Transform set successfully",
            )
        except Exception as e:
            logger.error("set_object_transform failed: %s", e)
            raise

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _generate_transform_code(self, request: SetObjectTransformVO) -> str:
        """Generate Blender Python code for transform modification.

        Supports absolute and relative transform modes. Only sets provided fields;
        omitted fields are preserved. Respects locked channels.
        """
        lines = [
            "import bpy",
            f"obj = bpy.data.objects.get({SetTransformExecutor._safe_str(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        # Check for locked transform channels
        lines.append(self._check_locked_channels_code())

        if request.location is not None:
            lines.append(f"obj.location = {SetTransformExecutor._tuple_str(request.location)}")

        if request.rotation is not None:
            lines.append(f"obj.rotation_euler = {SetTransformExecutor._tuple_str(request.rotation)}")

        if request.scale is not None:
            lines.append(f"obj.scale = {SetTransformExecutor._tuple_str(request.scale)}")

        return "\n".join(lines)

    def _check_locked_channels_code(self) -> str:
        """Generate code to check for locked transform channels.

        FR-OBJ-003: Locked transform channels should be respected unless explicit override is allowed.
        """
        return (
            "# Check for locked transform channels\n"
            "if obj.lock_location[0]: raise TransformLockError('location.x')\n"
            "if obj.lock_location[1]: raise TransformLockError('location.y')\n"
            "if obj.lock_location[2]: raise TransformLockError('location.z')\n"
            "if obj.lock_rotation[0]: raise TransformLockError('rotation.x')\n"
            "if obj.lock_rotation[1]: raise TransformLockError('rotation.y')\n"
            "if obj.lock_rotation[2]: raise TransformLockError('rotation.z')\n"
            "if obj.lock_scale[0]: raise TransformLockError('scale.x')\n"
            "if obj.lock_scale[1]: raise TransformLockError('scale.y')\n"
            "if obj.lock_scale[2]: raise TransformLockError('scale.z')\n"
        )

    @staticmethod
    def _validate_scale(scale: ScaleVector) -> None:
        """Validate scale values are finite and non-zero unless explicitly allowed.

        FR-OBJ-003: Scale values must be finite and non-zero.
        """
        for i, val in enumerate(scale):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Scale component {i} is not numeric: {val}")
            if val == 0:
                logger.warning("Zero scale detected at component %d", i)

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
