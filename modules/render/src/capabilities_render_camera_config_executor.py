"""Capability: Render camera configuration executor.

FR-RND-003: Configure camera.
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
    SuccessFlag,
)
from modules.shared.src.render.contract_render_camera_config_protocol import (
    IRenderCameraConfigProtocol,
)
from modules.shared.src.render.taxonomy_render_constant import (
    MAX_FOCAL_LENGTH,
    MIN_FOCAL_LENGTH,
    VALID_SENSOR_FITS,
)
from modules.shared.src.render.taxonomy_render_error import (
    RenderError,
    RenderErrorCategory,
)
from modules.shared.src.render.taxonomy_render_event import CameraConfiguredEvent
from modules.shared.src.render.taxonomy_render_vo import CameraConfigVO
from modules.shared.src.render.utility_render_code_builder import (
    build_camera_config_code,
)
from modules.shared.src.render.utility_render_result_parser import (
    parse_camera_config_result,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderCameraConfigExecutor(IRenderCameraConfigProtocol):
    """Capability for FR-RND-003: camera configuration."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._code_executor = code_executor

    # ─── Block 2: protocol methods only ───────────────────────
    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO:
        """Configure camera optical and selection behavior."""
        validation_error = self._validate(request)
        if validation_error is not None:
            return self._failure(request, validation_error.to_prompt())

        try:
            code = build_camera_config_code(request)
            raw = await self._execute_code(code)
            metrics = parse_camera_config_result(raw)

            if not str(metrics.resolved_camera_ref).strip():
                return self._failure(
                    request,
                    Prompt(
                        f"[{RenderErrorCategory.CAMERA_SETUP.value}] Camera configuration failed: camera not resolved"
                    ),
                )

            event = CameraConfiguredEvent(
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                camera_ref=metrics.resolved_camera_ref,
                focal_length=metrics.final_focal_length,
                active_status=metrics.active_status,
                depth_of_field_applied=metrics.depth_of_field_applied,
                message=Prompt("Camera configured"),
            )
            logger.info("camera_configured event=%s", event)

            return replace(
                request,
                success=SuccessFlag(True),
                resolved_camera_ref=metrics.resolved_camera_ref,
                final_focal_length=metrics.final_focal_length,
                active_status=metrics.active_status,
                depth_of_field_applied=metrics.depth_of_field_applied,
                message=Prompt("Camera configured"),
            )

        except Exception as exc:
            logger.exception("Camera configuration failed")
            return self._failure(
                request,
                Prompt(f"[{RenderErrorCategory.CAMERA_SETUP.value}] Camera configuration failed: {exc}"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    def _validate(self, request: CameraConfigVO) -> RenderError | None:
        focal_length = float(request.focal_length)

        if not (MIN_FOCAL_LENGTH <= focal_length <= MAX_FOCAL_LENGTH):
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(
                    f"focal_length must be between {MIN_FOCAL_LENGTH} and {MAX_FOCAL_LENGTH}"
                ),
            )

        if request.sensor_fit not in VALID_SENSOR_FITS:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid sensor_fit: {request.sensor_fit}"),
            )

        return None

    async def _execute_code(self, code: PythonCode) -> Prompt:
        return await self._code_executor.execute_python(code)

    def _failure(self, request: CameraConfigVO, message: Prompt) -> CameraConfigVO:
        return replace(request, success=SuccessFlag(False), message=message)

    def __repr__(self) -> str:
        return "RenderCameraConfigExecutor()"