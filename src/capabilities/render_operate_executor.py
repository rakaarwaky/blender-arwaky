"""Handler: Render and viewport capture operations."""

import json
import logging
import time

from contract import (
    BlenderPort,
    RenderOperateProtocol,
)
from taxonomy import (
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


def _py_str(value: str) -> str:
    """Safely escape a string for inclusion in generated Python code."""
    return json.dumps(str(value))


class RenderOperateExecutor(RenderOperateProtocol):
    """Business logic for rendering and visualization."""

    def __init__(self, blender_port: BlenderPort):
        self.blender = blender_port

    async def get_viewport_screenshot(self, request: GetScreenshotRequestVO) -> ScreenshotResponseVO:
        logger.info("Capturing viewport screenshot with max size %s", request.max_size)
        try:
            image_data, width, height = await self.blender.get_screenshot(max_size=request.max_size)
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

        loc = f"({location[0]}, {location[1]}, {location[2]})"
        rot = f"({rotation[0]}, {rotation[1]}, {rotation[2]})"

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
            tgt = f"({target[0]}, {target[1]}, {target[2]})"
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

        code = f"import bpy\nbpy.context.scene.render.engine = '{engine_str}'\n"

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

        rule_val = str(rule)
        code = (
            "import bpy\n"
            "camera = bpy.data.objects.get('Camera')\n"
            "if camera and camera.type == 'CAMERA':\n"
            "    camera.data.show_guide = True\n"
        )
        if rule_val == "thirds":
            code += "    camera.data.show_guide_rule_of_thirds = True\n"
        elif rule_val == "golden":
            code += "    camera.data.show_guide_golden_ratio = True\n"

        try:
            await self.blender.execute_code(PythonCode(code))
            return Prompt(f"Composition rule {rule} applied")
        except Exception as e:
            logger.error("apply_composition failed: %s", e)
            raise BlenderMCPError(ErrorMessage(f"Failed to apply composition: {e}")) from e

    async def render(self, request: RenderRequestVO) -> RenderResponseVO:
        logger.info("Rendering frame to %s", request.output_path)

        safe_path = _py_str(str(request.output_path))
        code = (
            "import bpy\n"
            f"bpy.context.scene.render.filepath = {safe_path}\n"
            "bpy.ops.render.render(write_still=True)\n"
        )
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
