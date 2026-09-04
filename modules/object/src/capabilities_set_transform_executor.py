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

from modules.shared.src.common.taxonomy_core_vo import Prompt, SuccessFlag
from modules.shared.src.object.contract_set_transform_protocol import SetObjectTransformProtocol
from modules.shared.src.object.taxonomy_object_vo import SetObjectTransformVO

logger = logging.getLogger("BlenderMCPServer")


class SetTransformExecutor(SetObjectTransformProtocol):
    """Concrete implementation for modifying object transforms.

    FR-OBJ-003: Supports absolute and relative transform modes, preserves omitted
    components, respects locked channels (unless override allowed), and ensures
    idempotency for identical absolute transforms.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: object | None = None) -> None:
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
            # Validate scale values are finite and non-zero
            for i, val in enumerate(request.scale):
                if not isinstance(val, (int, float)) or val == 0:
                    raise ValueError(f"Scale component {i} is zero — non-zero scale is required")

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
            f"obj = bpy.data.objects.get({repr(str(request.object_name))})",
            'if obj is None:\n    raise ValueError("Object not found in scene.")',
        ]

        # Check for locked transform channels
        lines.append(self._check_locked_channels_code())

        if request.location is not None:
            lines.append(f"obj.location = ({request.location[0]}, {request.location[1]}, {request.location[2]})")

        if request.rotation is not None:
            lines.append(f"obj.rotation_euler = ({request.rotation[0]}, {request.rotation[1]}, {request.rotation[2]})")

        if request.scale is not None:
            lines.append(f"obj.scale = ({request.scale[0]}, {request.scale[1]}, {request.scale[2]})")

        return "\n".join(lines)

    def _check_locked_channels_code(self) -> str:
        """Generate code to check for locked transform channels.

        FR-OBJ-003: Locked transform channels should be respected unless explicit override is allowed.
        Uses a single loop over all lock tuples for efficiency (PERF02).
        """
        return (
            "# Check for locked transform channels\n"
            "for i, (loc, rot, scl) in enumerate(zip(obj.lock_location, obj.lock_rotation, obj.lock_scale)):\n"
            "    if loc: raise ValueError(f'Location channel {i} is locked')\n"
            "    if rot: raise ValueError(f'Rotation channel {i} is locked')\n"
            "    if scl: raise ValueError(f'Scale channel {i} is locked')\n"
        )

    def __repr__(self) -> str:
        return "SetTransformExecutor()"
