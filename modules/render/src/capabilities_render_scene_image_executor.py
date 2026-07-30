"""Capability: Render scene image executor.

FR-RND-002: Render scene image.
"""

from __future__ import annotations

import logging
from dataclasses import replace

from modules.shared.src.common.taxonomy_core_vo import (
    Prompt,
    PythonCode,
    RenderEngine,
    SuccessFlag,
)
from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.job.contract_job_capacity_protocol import (
    IJobCapacity,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CapacityDecision,
    JobPolicy,
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
from modules.shared.src.security.contract_validate_path_protocol import (
    ValidatePathProtocol,
)
from modules.shared.src.security.taxonomy_security_vo import (
    AccessMode,
    PathValidationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderSceneImageExecutor(IRenderSceneImageProtocol):
    """Capability for FR-RND-002: scene render."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        security_validator: ValidatePathProtocol | None = None,
        job_capacity: IJobCapacity | None = None,
        event_emitter: object | None = None,
    ) -> None:
        self._code_executor = code_executor
        self._security_validator = security_validator
        self._job_capacity = job_capacity
        self._event_emitter = event_emitter

    # ─── Block 2: protocol methods only ───────────────────────
    async def render_scene(self, request: RenderSceneVO) -> RenderSceneVO:
        """Render scene to image artifact."""
        normalized = self._normalize(request)

        validation_error = self._validate(normalized)
        if validation_error is not None:
            return self._failure(normalized, validation_error.to_prompt())

        # FR-RND-002: Output destination validated through security before render begins
        try:
            await self._validate_security(str(normalized.output_path))
        except Exception as exc:
            logger.warning("Security path validation failed: %s", exc)
            return self._failure(
                normalized,
                Prompt(f"[{RenderErrorCategory.SECURITY_VIOLATION.value}] Path validation failed: {exc}"),
            )

        # FR-RND-002: Background render eligibility — check capacity before execution
        if bool(normalized.background):
            capacity_check = await self._check_job_capacity()
            if not capacity_check.accepted:
                return self._failure(
                    normalized,
                    Prompt(f"[{RenderErrorCategory.CAPACITY.value}] {capacity_check.reason}"),
                )

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

            if self._event_emitter is not None:
                try:
                    await self._event_emitter.emit(event)
                except Exception:
                    logger.warning("Failed to emit SceneRenderCompletedEvent")

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

            if self._event_emitter is not None:
                try:
                    await self._event_emitter.emit(failed_event)
                except Exception:
                    logger.warning("Failed to emit SceneRenderFailedEvent")

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

    async def _validate_security(self, path: str) -> None:
        """Validate output path through security policy (FR-RND-002)."""
        if self._security_validator is None:
            return
        request = PathValidationVO(
            target_path=path,
            access_mode=AccessMode.WRITE,
        )
        result = await self._security_validator.validate_path(request)
        if not result.allowed:
            raise Exception(result.denial_reason or "Path validation denied by security policy")

    async def _check_job_capacity(self) -> CapacityDecision:
        """Check job capacity before submitting background render (FR-RND-002)."""
        if self._job_capacity is None:
            return CapacityDecision(
                accepted=True,
                active=0,
                limit=100,
                available=100,
                reason="",
            )

        policy = JobPolicy()
        result = self._job_capacity.evaluate(active_count=0, policy=policy)
        if not result.accepted:
            return result

        return result

    async def _execute_code(self, code: PythonCode) -> Prompt:
        return await self._code_executor.execute_python(code)

    def _failure(self, request: RenderSceneVO, message: Prompt) -> RenderSceneVO:
        return replace(request, success=SuccessFlag(False), message=message)

    def __repr__(self) -> str:
        return "RenderSceneImageExecutor()"
