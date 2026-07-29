"""Capability: Render viewport capture executor.

FR-RND-001: Capture viewport screenshot.
"""

from __future__ import annotations

import logging
import time
from dataclasses import replace

from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.common.taxonomy_core_vo import (
    DurationMs,
    Prompt,
    PythonCode,
    SuccessFlag,
)
from modules.shared.src.render.contract_render_viewport_capture_protocol import (
    IRenderViewportCaptureProtocol,
)
from modules.shared.src.render.taxonomy_render_constant import (
    VALID_IMAGE_FORMATS,
    VALID_OVERWRITE_POLICIES,
    VALID_SHADING_MODES,
    VALID_VIEW_ANGLES,
)
from modules.shared.src.render.taxonomy_render_error import (
    RenderError,
    RenderErrorCategory,
)
from modules.shared.src.render.taxonomy_render_event import ViewportCapturedEvent
from modules.shared.src.render.taxonomy_render_vo import ViewportCaptureVO
from modules.shared.src.render.utility_render_code_builder import (
    build_viewport_capture_code,
)
from modules.shared.src.render.utility_render_result_parser import (
    parse_artifact_result,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderViewportCaptureExecutor(IRenderViewportCaptureProtocol):
    """Capability for FR-RND-001: viewport capture."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._code_executor = code_executor

    # ─── Block 2: protocol methods only ───────────────────────
    async def capture_viewport(self, request: ViewportCaptureVO) -> ViewportCaptureVO:
        """Capture viewport as image artifact."""
        validation_error = self._validate(request)
        if validation_error is not None:
            return self._failure(request, validation_error.to_prompt())

        try:
            start_time = time.perf_counter()
            code = build_viewport_capture_code(request)
            raw = await self._execute_code(code)
            artifact_path, width, height, resolved_format = parse_artifact_result(raw)
            duration_ms = DurationMs(round((time.perf_counter() - start_time) * 1000.0, 1))

            event = ViewportCapturedEvent(
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                artifact_path=artifact_path,
                image_format=resolved_format,
                width=width,
                height=height,
                duration_ms=duration_ms,
                message=Prompt("Viewport capture completed"),
            )
            logger.info("viewport_captured event=%s", event)

            return replace(
                request,
                success=SuccessFlag(True),
                artifact_path=artifact_path,
                resolved_format=resolved_format,
                width=width,
                height=height,
                duration_ms=duration_ms,
                message=Prompt("Viewport capture completed"),
            )

        except Exception as exc:
            logger.exception("Viewport capture failed")
            return self._failure(
                request,
                Prompt(f"[{RenderErrorCategory.RENDER_OUTPUT.value}] Viewport capture failed: {exc}"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    def _validate(self, request: ViewportCaptureVO) -> RenderError | None:
        if not str(request.output_path).strip():
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt("Viewport capture output_path is required"),
            )

        if request.view_angle not in VALID_VIEW_ANGLES:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid view_angle: {request.view_angle}"),
            )

        if request.shading not in VALID_SHADING_MODES:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid shading mode: {request.shading}"),
            )

        if str(request.image_format).upper() not in VALID_IMAGE_FORMATS:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid image format: {request.image_format}"),
            )

        if request.overwrite_policy not in VALID_OVERWRITE_POLICIES:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid overwrite policy: {request.overwrite_policy}"),
            )

        return None

    async def _execute_code(self, code: PythonCode) -> Prompt:
        return await self._code_executor.execute_python(code)

    def _failure(self, request: ViewportCaptureVO, message: Prompt) -> ViewportCaptureVO:
        return replace(request, success=SuccessFlag(False), message=message)

    def __repr__(self) -> str:
        return "RenderViewportCaptureExecutor()"