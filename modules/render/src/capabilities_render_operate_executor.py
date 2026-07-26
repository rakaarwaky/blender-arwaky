"""Capability: Render operation executor.

Implements RenderOperateProtocol — handles viewport capture, camera setup,
render configuration, composition rules, and frame rendering through
the server module's code execution capability.
"""

from __future__ import annotations

import json
import logging
import time

from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    Prompt,
    RenderEngine,
    RenderSamples,
    RotationVector,
    RuleName,
    SuccessFlag,
    UseDenoising,
)
from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    GetScreenshotVO,
    RenderVO,
)

logger = logging.getLogger("BlenderMCPServer")


def _py_str(value: object) -> str:
    """Safely escape a value for inclusion in generated Python code."""
    return json.dumps(str(value))


def _format_coord(coord: object) -> str:
    """Safely format a coordinate value as a float for Python code."""
    return str(float(coord))


class RenderOperateExecutor(RenderOperateProtocol):
    """Business logic for rendering and visualization."""

    def __init__(self, code_executor: Prompt) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor

    async def get_viewport_screenshot(self, request: GetScreenshotVO) -> GetScreenshotVO:
        logger.info(
            "Capturing viewport screenshot: max_size=%s, view=%s, shading=%s, overlays=%s, focus=%s",
            request.max_size,
            request.view_angle,
            request.shading,
            request.show_overlays,
            request.focus_object,
        )
        # Screenshot requires direct socket access — delegate to server module
        raise NotImplementedError("Viewport capture requires socket adapter; not available through code executor")

    async def setup_camera(
        self,
        location: CoordinateList,
        rotation: RotationVector,
        target: CoordinateList | None = None,
    ) -> Prompt:
        logger.info("Setting up camera at %s", location)

        loc = f"({_format_coord(location[0])}, {_format_coord(location[1])}, {_format_coord(location[2])})"
        rot = f"({_format_coord(rotation[0])}, {_format_coord(rotation[1])}, {_format_coord(rotation[2])})"

        code = (
            "import bpy\n"
            "camera = bpy.data.objects.get('Camera')\n"
            "if not camera:\n"
            "    bpy.ops.object.camera_add()\n"
            "    camera = bpy.context.active_object\n"
            f"camera.location = {loc}\n"
            f"camera.rotation_euler = {rot}\n"
        )
        if target is not None:
            tgt = f"({_format_coord(target[0])}, {_format_coord(target[1])}, {_format_coord(target[2])})"
            code += (
                "target_name = 'MCP_CameraTarget'\n"
                "target_obj = bpy.data.objects.get(target_name)\n"
                "if not target_obj:\n"
                "    bpy.ops.object.empty_add(type='PLAIN_AXES')\n"
                "    target_obj = bpy.context.active_object\n"
                "    target_obj.name = target_name\n"
                f"target_obj.location = {tgt}\n"
                "constraint = camera.constraints.get('Track To')\n"
                "if not constraint:\n"
                "    constraint = camera.constraints.new(type='TRACK_TO')\n"
                "constraint.target = target_obj\n"
                "constraint.track_axis = 'TRACK_NEGATIVE_Z'\n"
                "constraint.up_axis = 'UP_Y'\n"
            )
        try:
            await self._execute_code(code)
            return Prompt("Camera setup successful")
        except Exception as e:
            logger.error("setup_camera failed: %s", e)
            raise RuntimeError(f"Failed to setup camera: {e}") from e

    async def setup_render(
        self,
        engine: RenderEngine | None = None,
        samples: RenderSamples | None = None,
        resolution: CoordinateList | None = None,
        use_denoising: UseDenoising | None = None,
    ) -> Prompt:
        engine = engine or RenderEngine("CYCLES")
        samples = samples or RenderSamples(128)
        use_denoising = use_denoising or UseDenoising(True)
        engine_str = str(engine).upper()
        logger.info("Setting up render engine: %s", engine_str)

        safe_engine = _py_str(engine_str)
        code = f"import bpy\nbpy.context.scene.render.engine = {safe_engine}\n"

        if engine_str == "CYCLES":
            denoise = "True" if use_denoising else "False"
            code += (
                f"bpy.context.scene.cycles.samples = {int(samples)}\n"
                f"bpy.context.scene.cycles.use_denoising = {denoise}\n"
            )
        if resolution is not None:
            code += (
                f"bpy.context.scene.render.resolution_x = {int(resolution[0])}\n"
                f"bpy.context.scene.render.resolution_y = {int(resolution[1])}\n"
            )
        try:
            await self._execute_code(code)
            return Prompt(f"Render configured for {engine_str}")
        except Exception as e:
            logger.error("setup_render failed: %s", e)
            raise RuntimeError(f"Failed to configure render: {e}") from e

    async def apply_composition(self, rule: RuleName | None = None) -> Prompt:
        rule = rule or RuleName("thirds")
        logger.info("Applying composition rule: %s", rule)

        rule_val = str(rule).lower()
        guide_set = "{'THIRDS'}" if rule_val == "thirds" else "{'GOLDEN'}" if rule_val == "golden" else "set()"
        if rule_val not in ("thirds", "golden"):
            logger.warning("Unknown composition rule '%s', applying empty guide set.", rule_val)

        code = (
            "import bpy\n"
            "camera = bpy.data.objects.get('Camera')\n"
            "if camera and camera.type == 'CAMERA':\n"
            f"    camera.data.show_guide = {guide_set}\n"
        )

        try:
            await self._execute_code(code)
            return Prompt(f"Composition rule {rule} applied")
        except Exception as e:
            logger.error("apply_composition failed: %s", e)
            raise RuntimeError(f"Failed to apply composition: {e}") from e

    async def render(self, request: RenderVO) -> RenderVO:
        logger.info("Rendering frame to %s", request.output_path)

        safe_path = _py_str(str(request.output_path))
        code = f"import bpy\nbpy.context.scene.render.filepath = {safe_path}\nbpy.ops.render.render(write_still=True)\n"
        try:
            start_time = time.perf_counter()
            await self._execute_code(code)
            render_time = round(time.perf_counter() - start_time, 2)
            return RenderVO(
                output_path=request.output_path,
                resolution_x=request.resolution_x,
                resolution_y=request.resolution_y,
                samples=request.samples,
                use_denoising=request.use_denoising,
                success=SuccessFlag(True),
                image_path=request.output_path,
                render_time=render_time,
                message="Render complete",
            )
        except Exception as e:
            logger.error("Render failed: %s", e)
            raise RuntimeError(f"Render failed: {e}") from e

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
                logger.info("Code execution result: %s", result[:200])
        else:
            raise RuntimeError(f"Unexpected code_executor type: {type(self._code_executor)}")