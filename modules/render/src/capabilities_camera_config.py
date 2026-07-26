"""Capability: Camera configuration executor.

Implements CameraConfigProtocol — handles camera positioning, orientation,
and lens settings through the server module's code execution capability.
"""

from __future__ import annotations

import json
import logging

from modules.shared.src.common.taxonomy_core_vo import Prompt
from modules.shared.src.render.contract_camera_config_protocol import CameraConfigProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    CameraConfigVO,
    CameraSetupVO,
)

logger = logging.getLogger("BlenderMCPServer")


def _format_coord_list(coords: list[float]) -> str:
    """Format a coordinate list as a Python tuple string."""
    return f"({_format_float(coords[0])}, {_format_float(coords[1])}, {_format_float(coords[2])})"


def _format_float(value: float) -> str:
    """Format a float value for Python code."""
    return str(float(value))


class CameraConfigExecutor(CameraConfigProtocol):
    """Business logic for camera configuration and positioning."""

    def __init__(self, code_executor: object) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def configure_camera(self, request: CameraSetupVO) -> CameraConfigVO:
        """Position and configure a scene camera.

        FR-RND-003: Creates camera if none exists (when policy allows).
        Resolves multiple cameras deterministically.
        Returns resolved camera reference and final settings.

        Args:
            request: Camera setup parameters including position, rotation,
                focal length, and framing target.

        Returns:
            Camera configuration result with success status and final settings.
        """
        logger.info(
            "Configuring camera: name=%s, location=(%s, %s, %s), rotation=(%s, %s, %s), focal=%.1f",
            request.camera_name or "auto",
            request.location_x,
            request.location_y,
            request.location_z,
            request.rotation_x,
            request.rotation_y,
            request.rotation_z,
            request.focal_length,
        )

        camera_name = request.camera_name or "MCP_Camera"
        safe_name = json.dumps(camera_name)
        loc = f"({_format_float(request.location_x)}, {_format_float(request.location_y)}, {_format_float(request.location_z)})"
        rot = f"({_format_float(request.rotation_x)}, {_format_float(request.rotation_y)}, {_format_float(request.rotation_z)})"

        code = (
            "import bpy\n"
            f"camera_name = {safe_name}\n"
            # Find existing camera by name
            "camera = bpy.data.objects.get(camera_name)\n"
            "if camera is None:\n"
            "    bpy.ops.object.camera_add()\n"
            "    camera = bpy.context.active_object\n"
            f"    camera.name = {safe_name}\n"
            # Set transform
            f"camera.location = {loc}\n"
            f"camera.rotation_euler = {rot}\n"
            # Set focal length
            f"camera.data.lens = {request.focal_length}\n"
        )

        # Set as active camera if requested
        if request.is_active:
            code += "bpy.context.scene.camera = camera\n"

        # Handle framing target
        if request.framing_target is not None:
            safe_target = json.dumps(request.framing_target)
            code += (
                f"target_name = {safe_target}\n"
                "target_obj = bpy.data.objects.get(target_name)\n"
                "if target_obj:\n"
                "    constraint = camera.constraints.get('Track To')\n"
                "    if not constraint:\n"
                "        constraint = camera.constraints.new(type='TRACK_TO')\n"
                "        constraint.name = 'Track To'\n"
                "        constraint.track_axis = 'TRACK_NEGATIVE_Z'\n"
                "        constraint.up_axis = 'UP_Y'\n"
                f"    constraint.target = target_obj\n"
            )

        try:
            await self._execute_code(code)
            final_settings = {
                "name": camera_name,
                "location": [request.location_x, request.location_y, request.location_z],
                "rotation": [request.rotation_x, request.rotation_y, request.rotation_z],
                "focal_length": request.focal_length,
                "is_active": request.is_active,
            }
            if request.framing_target is not None:
                final_settings["framing_target"] = request.framing_target

            logger.info("Camera configured successfully: %s", camera_name)
            return CameraConfigVO(
                success=True,  # type: ignore[call-arg]
                camera_name=camera_name,
                final_settings=final_settings,
                message=Prompt(f"Camera '{camera_name}' configured successfully"),
            )
        except Exception as e:
            logger.error("Camera configuration failed: %s", e)
            return CameraConfigVO(
                success=False,  # type: ignore[call-arg]
                camera_name=camera_name,
                final_settings={},
                message=Prompt(f"Camera configuration failed: {e}"),
            )

    async def _execute_code(self, code: str) -> None:
        """Execute Python code through the server module's code execution capability.

        Args:
            code: Python code string to execute in Blender.

        Raises:
            RuntimeError: If code execution fails.
        """
        if callable(self._code_executor):
            result = await self._code_executor(code)
            if isinstance(result, str):
                logger.info("Camera config code execution: %s", result[:200])
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")
