"""Capability: Render scene image executor.

FR-RND-002: Render scene image.
"""

from __future__ import annotations

import logging
from dataclasses import replace

from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.common.taxonomy_core_vo import (
    Prompt,
    PythonCode,
    RenderEngine,
    SuccessFlag,
)
from modules.shared.src.render.contract_render_scene_image_protocol import (
    IRenderSceneImageProtocol,
)
from modules.shared.src.render.taxonomy_render_constant import (
    MAX_RESOLUTION,
    MAX_SAMPLES,
    MIN_RESOLUTION,
    MIN_SAMPLES,
    RENDER_ENGINE_CYCLES,
    VALID_OVERWRITE_POLICIES,
    VALID_RENDER_ENGINES,
)
from modules.shared.src.render.taxonomy_render_error import (
    RenderError,
    RenderErrorCategory,
)
from modules.shared.src.render.taxonomy_render_event import (
    SceneRenderCompletedEvent,
    SceneRenderFailedEvent,
)
from modules.shared.src.render.taxonomy_render_vo import RenderSceneVO
from modules.shared.src.render.utility_render_code_builder import (
    build_scene_render_code,
)
from modules.shared.src.render.utility_render_result_parser import parse_render_result

logger = logging.getLogger("BlenderMCPServer")


class RenderSceneImageExecutor(IRenderSceneImageProtocol):
    """Capability for FR-RND-002: scene render."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._code_executor = code_executor

    # ─── Block 2: protocol methods only ───────────────────────
    async def render_scene(self, request: RenderSceneVO) -> RenderSceneVO:
        """Render scene to image artifact."""
        normalized = self._normalize(request)

        validation_error = self._validate(normalized)
        if validation_error is not None:
            return self._failure(normalized, validation_error.to_prompt())

        try:
            code = build_scene_render_code(normalized)
            raw = await self._execute_code(code)
            metrics = parse_render_result(raw)

            event = SceneRenderCompletedEvent(
                correlation_id=normalized.correlation_id,
                success=SuccessFlag(True),
                artifact_path=metrics.artifact_path,
                render_time=metrics.render_time,
                final_resolution_x=metrics.width,
                final_resolution_y=metrics.height,
                engine_used=metrics.engine_used,
                denoising_applied=metrics.denoising_applied,
                task_ref=None,
                message=Prompt("Scene render completed"),
            )
            logger.info("scene_render_completed event=%s", event)

            return replace(
                normalized,
                success=SuccessFlag(True),
                artifact_path=metrics.artifact_path,
                render_time=metrics.render_time,
                final_resolution_x=metrics.width,
                final_resolution_y=metrics.height,
                engine_used=metrics.engine_used,
                denoising_applied=metrics.denoising_applied,
                task_ref=None,
                message=Prompt("Scene render completed"),
            )

        except Exception as exc:
            logger.exception("Scene render failed")

            failed_event = SceneRenderFailedEvent(
                correlation_id=normalized.correlation_id,
                success=SuccessFlag(False),
                error_category=RenderErrorCategory.RENDER_OUTPUT,
                phase="execution",
                message=Prompt(str(exc)),
            )
            logger.info("scene_render_failed event=%s", failed_event)

            return self._failure(
                normalized,
                Prompt(f"[{RenderErrorCategory.RENDER_OUTPUT.value}] Scene render failed: {exc}"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    def _normalize(self, request: RenderSceneVO) -> RenderSceneVO:
        engine = str(request.render_engine).upper()

        if engine not in VALID_RENDER_ENGINES:
            return replace(request, render_engine=RenderEngine(RENDER_ENGINE_CYCLES))

        return replace(request, render_engine=RenderEngine(engine))

    def _validate(self, request: RenderSceneVO) -> RenderError | None:
        if not str(request.output_path).strip():
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt("Render output_path is required"),
            )

        if not (MIN_RESOLUTION <= int(request.resolution_x) <= MAX_RESOLUTION):
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"resolution_x must be between {MIN_RESOLUTION} and {MAX_RESOLUTION}"),
            )

        if not (MIN_RESOLUTION <= int(request.resolution_y) <= MAX_RESOLUTION):
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"resolution_y must be between {MIN_RESOLUTION} and {MAX_RESOLUTION}"),
            )

        if not (MIN_SAMPLES <= int(request.samples) <= MAX_SAMPLES):
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"samples must be between {MIN_SAMPLES} and {MAX_SAMPLES}"),
            )

        if request.overwrite_policy not in VALID_OVERWRITE_POLICIES:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid overwrite policy: {request.overwrite_policy}"),
            )

        return None

    async def _execute_code(self, code: PythonCode) -> Prompt:
        return await self._code_executor.execute_python(code)

    def _failure(self, request: RenderSceneVO, message: Prompt) -> RenderSceneVO:
        return replace(request, success=SuccessFlag(False), message=message)

    def __repr__(self) -> str:
        return "RenderSceneImageExecutor()"