"""Handler: Render and viewport capture operations."""

import json
import logging
import time

from modules.shared.src import BlenderPort, RenderOperateProtocol
from modules.shared.src import (
    BlenderMCPError,
    CoordinateList,
    ErrorMessage,
    GetScreenshotRequestVO,
    ImageFormat,
    Prompt,
    PythonCode,
    RenderEngine,
    RenderRequestVO,
    RenderResponseVO,
    RenderSamples,
    ResolutionX,
    ResolutionY,
    RotationVector,
    RuleName,
    ScreenshotResponseVO,
    SuccessFlag,
    UseDenoising,
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

    def __init__(self, blender_port: BlenderPort):
        self.blender = blender_port

    async def get_viewport_screenshot(self, request: GetScreenshotRequestVO) -> ScreenshotResponseVO:
        logger.info(
            "Capturing viewport screenshot: max_size=%s, view=%s, shading=%s, overlays=%s, focus=%s",
            request.max_size,
            request.view_angle,
            request.shading,
            request.show_overlays,
            request.focus_object,
        )
        try:
            image_data, width, height = await self.blender.get_screenshot(
                max_size=request.max_size,
                view_angle=request.view_angle,
                shading_mode=request.shading,
                show_overlays=request.show_overlays,
                focus_object=request.focus_object,
            )
            return ScreenshotResponseVO(
                success=SuccessFlag(True),
                image_data=image_data,
                format=request.format or ImageFormat("png"),
                width=ResolutionX(width),
                height=ResolutionY(height),
            )
        except Exception as e:
            logger.error("Failed to capture screenshot: %s", e)
            raise BlenderMCPError(ErrorMessage(f"Screenshot failed: {e}")) from e

    async def setup_camera(
        self, location: CoordinateList, rotation: RotationVector, target: CoordinateList | None = None
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
            await self.blender.execute_code(PythonCode(code))
            return Prompt("Camera setup successful")
        except Exception as e:
            logger.error("setup_camera failed: %s", e)
            raise BlenderMCPError(ErrorMessage(f"Failed to setup camera: {e}")) from e

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
            await self.blender.execute_code(PythonCode(code))
            return Prompt(f"Render configured for {engine_str}")
        except Exception as e:
            logger.error("setup_render failed: %s", e)
            raise BlenderMCPError(ErrorMessage(f"Failed to configure render: {e}")) from e

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
            await self.blender.execute_code(PythonCode(code))
            return Prompt(f"Composition rule {rule} applied")
        except Exception as e:
            logger.error("apply_composition failed: %s", e)
            raise BlenderMCPError(ErrorMessage(f"Failed to apply composition: {e}")) from e

    async def render(self, request: RenderRequestVO) -> RenderResponseVO:
        logger.info("Rendering frame to %s", request.output_path)

        safe_path = _py_str(str(request.output_path))
        code = f"import bpy\nbpy.context.scene.render.filepath = {safe_path}\nbpy.ops.render.render(write_still=True)\n"
        try:
            start_time = time.perf_counter()
            await self.blender.execute_code(PythonCode(code))
            render_time = round(time.perf_counter() - start_time, 2)
            return RenderResponseVO(
                success=SuccessFlag(True),
                image_path=request.output_path,
                render_time=render_time,
                message="Render complete",
            )
        except Exception as e:
            logger.error("Render failed: %s", e)
            raise BlenderMCPError(ErrorMessage(f"Render failed: {e}")) from e
