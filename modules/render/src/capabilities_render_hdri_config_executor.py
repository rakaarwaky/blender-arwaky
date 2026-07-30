"""Capability: Render HDRI configuration executor.

FR-RND-004: Configure HDRI lighting.
"""

from __future__ import annotations

import logging
from dataclasses import replace

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    LightStrength,
    Prompt,
    PythonCode,
    SuccessFlag,
)
from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.render.contract_render_hdri_config_protocol import (
    IRenderHdriConfigProtocol,
)
from modules.shared.src.render.taxonomy_render_constant import (
    MAX_HDRI_STRENGTH,
    MIN_HDRI_STRENGTH,
    VALID_OVERWRITE_POLICIES,
)
from modules.shared.src.render.taxonomy_render_error import (
    RenderError,
    RenderErrorCategory,
)
from modules.shared.src.render.taxonomy_render_event import HdriLightingConfiguredEvent
from modules.shared.src.render.taxonomy_render_vo import HdriConfigVO, RotationDegrees
from modules.shared.src.render.utility_render_code_builder import (
    build_hdri_config_code,
)
from modules.shared.src.render.utility_render_result_parser import (
    parse_hdri_config_result,
)
from modules.shared.src.security.contract_validate_path_protocol import (
    ValidatePathProtocol,
)
from modules.shared.src.security.taxonomy_security_vo import (
    AccessMode,
    PathValidationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderHdriConfigExecutor(IRenderHdriConfigProtocol):
    """Capability for FR-RND-004: HDRI configuration."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        security_validator: ValidatePathProtocol | None = None,
        event_emitter: object | None = None,
    ) -> None:
        self._code_executor = code_executor
        self._security_validator = security_validator
        self._event_emitter = event_emitter

    # ─── Block 2: protocol methods only ───────────────────────
    async def configure_hdri(self, request: HdriConfigVO) -> HdriConfigVO:
        """Configure HDRI-based environment lighting."""
        normalized = self._normalize(request)

        validation_error = self._validate(normalized)
        if validation_error is not None:
            return self._failure(normalized, validation_error.to_prompt())

        # FR-RND-004: Local HDRI file ref validated through security before use
        try:
            await self._validate_security(str(normalized.hdri_path))
        except Exception as exc:
            logger.warning("Security path validation failed: %s", exc)
            return self._failure(
                normalized,
                Prompt(f"[{RenderErrorCategory.SECURITY_VIOLATION.value}] Path validation failed: {exc}"),
            )

        try:
            code = build_hdri_config_code(normalized)
            raw = await self._execute_code(code)
            metrics = parse_hdri_config_result(raw)

            if not str(metrics.environment_ref).strip():
                return self._failure(
                    normalized,
                    Prompt(
                        f"[{RenderErrorCategory.ENVIRONMENT_STATE.value}] HDRI configuration failed: environment not resolved"
                    ),
                )

            event = HdriLightingConfiguredEvent(
                correlation_id=normalized.correlation_id,
                success=SuccessFlag(True),
                environment_ref=metrics.environment_ref,
                strength=metrics.applied_strength,
                rotation=metrics.applied_rotation,
                message=Prompt("HDRI lighting configured"),
            )

            if self._event_emitter is not None:
                try:
                    await self._event_emitter.emit(event)
                except Exception:
                    logger.warning("Failed to emit HdriLightingConfiguredEvent")

            logger.info("hdri_lighting_configured event=%s", event)

            return replace(
                normalized,
                success=SuccessFlag(True),
                environment_ref=metrics.environment_ref,
                applied_strength=metrics.applied_strength,
                applied_rotation=metrics.applied_rotation,
                message=Prompt("HDRI lighting configured"),
            )

        except Exception as exc:
            logger.exception("HDRI configuration failed")
            return self._failure(
                normalized,
                Prompt(f"[{RenderErrorCategory.ENVIRONMENT_STATE.value}] HDRI configuration failed: {exc}"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    def _normalize(self, request: HdriConfigVO) -> HdriConfigVO:
        normalized_rotation = float(request.rotation) % 360.0

        return replace(
            request,
            strength=LightStrength(float(request.strength)),
            rotation=RotationDegrees(normalized_rotation),
        )

    def _validate(self, request: HdriConfigVO) -> RenderError | None:
        if not str(request.hdri_path).strip():
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt("HDRI path is required"),
            )

        strength = float(request.strength)
        if not (MIN_HDRI_STRENGTH <= strength <= MAX_HDRI_STRENGTH):
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(
                    f"HDRI strength must be between {MIN_HDRI_STRENGTH} and {MAX_HDRI_STRENGTH}"
                ),
            )

        if request.overwrite_policy not in VALID_OVERWRITE_POLICIES:
            return RenderError(
                category=RenderErrorCategory.VALIDATION,
                message=Prompt(f"Invalid overwrite policy: {request.overwrite_policy}"),
            )

        return None

    async def _validate_security(self, path: str) -> None:
        """Validate HDRI file path through security policy (FR-RND-004)."""
        if self._security_validator is None:
            return
        request = PathValidationVO(
            target_path=path,
            access_mode=AccessMode.READ,
        )
        result = await self._security_validator.validate_path(request)
        if not result.allowed:
            raise Exception(result.denial_reason or "Path validation denied by security policy")

    async def _execute_code(self, code: PythonCode) -> Prompt:
        return await self._code_executor.execute_python(code)

    def _failure(self, request: HdriConfigVO, message: Prompt) -> HdriConfigVO:
        return replace(request, success=SuccessFlag(False), message=message)

    def __repr__(self) -> str:
        return "RenderHdriConfigExecutor()"
