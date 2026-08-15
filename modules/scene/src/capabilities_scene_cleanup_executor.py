"""Capability: Scene cleanup executor.

FR-SCN-002: Execute scene cleanup (execution + parsing only).
Policy resolution delegated to utility.

Capabilities layer:
- implements protocol ABC
- 3-block structure
- owns execution and parsing only
- delegates validation/policy to utility
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import Prompt, PythonCode, SuccessFlag
from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.scene.contract_scene_cleanup_protocol import ISceneCleanupProtocol
from modules.shared.src.scene.taxonomy_scene_constant import (
    CHILD_POLICY_DELETE,
    CHILD_POLICY_DETACH,
    CHILD_POLICY_REJECT,
    CLEANUP_CONFIRMATION_REQUIRED,
    DEPENDENT_POLICY_IGNORE,
    DEPENDENT_POLICY_REJECT,
    DEPENDENT_POLICY_REMOVE_SAFE,
)
from modules.shared.src.scene.taxonomy_scene_error import SceneError, SceneErrorCategory
from modules.shared.src.scene.taxonomy_scene_event import (
    SceneCleanupCompletedEvent,
    SceneCleanupDryRunCompletedEvent,
    SceneCleanupFailedEvent,
)
from modules.shared.src.scene.taxonomy_scene_vo import (
    ObjectCount,
    SceneCleanupMetricsVO,
    SceneCleanupPolicyVO,
    SceneCleanupVO,
)
from modules.shared.src.scene.utility_scene_code_builder import build_cleanup_code
from modules.shared.src.scene.utility_scene_result_parser import parse_cleanup_metrics

logger = logging.getLogger(__name__)


class SceneCleanupExecutor(ISceneCleanupProtocol):
    """Capability for FR-SCN-002: scene cleanup execution and parsing."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        event_emitter: object | None = None,
    ) -> None:
        if code_executor is None:
            raise ValueError("code_executor must be provided")
        self._code_executor = code_executor
        self._event_emitter = event_emitter

    # ─── Block 2: protocol methods only ───────────────────────
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup or dry-run preview."""
        # Pre-flight validation — FR-SCN-002 confirmation rule
        pre_flight_error = self._pre_flight_check(request)
        if pre_flight_error is not None:
            return self._failure(request, pre_flight_error.to_prompt())

        try:
            preservation = set(request.preservation_list)
            policy = SceneCleanupPolicyVO(
                mode=request.mode,
                preserve_cameras=True,  # FR-SCN-002: cameras are always protected regardless of preservation list
                preserve_lights="light" in preservation,
                include_hidden_objects=request.include_hidden_objects,
                child_handling_policy=request.child_handling_policy,
                dependent_handling_policy=request.dependent_handling_policy,
                protect_active_camera=True,
                protect_sole_camera=True,
            )
            code = build_cleanup_code(policy, request.dry_run)

            raw = await self._execute_code(code)
            metrics = parse_cleanup_metrics(raw)

            if request.dry_run:
                logger.info(
                    "scene_cleanup_dry_run_completed removed=%d preserved=%d",
                    metrics.removed_count,
                    metrics.preserved_count,
                )

                # FR-SCN-002: emit dry-run completed event
                if self._event_emitter:
                    try:
                        await self._event_emitter.emit(
                            SceneCleanupDryRunCompletedEvent(
                                correlation_id=request.correlation_id,
                                success=SuccessFlag(True),
                                mode=request.mode,
                                removable_count=metrics.removed_count,
                                preserved_count=metrics.preserved_count,
                                skipped_count=metrics.skipped_count,
                                message=Prompt("Scene cleanup dry-run completed"),
                            )
                        )
                    except Exception:
                        logger.warning("Failed to emit SceneCleanupDryRunCompletedEvent")

                return self._build_result(request, metrics, "Dry-run completed")

            logger.info(
                "scene_cleanup_completed removed=%d preserved=%d", metrics.removed_count, metrics.preserved_count
            )

            # FR-SCN-002: emit cleanup completed event
            if self._event_emitter:
                try:
                    await self._event_emitter.emit(
                        SceneCleanupCompletedEvent(
                            correlation_id=request.correlation_id,
                            success=SuccessFlag(True),
                            mode=request.mode,
                            removed_count=metrics.removed_count,
                            preserved_count=metrics.preserved_count,
                            skipped_count=metrics.skipped_count,
                            message=Prompt("Scene cleanup completed"),
                        )
                    )
                except Exception:
                    logger.warning("Failed to emit SceneCleanupCompletedEvent")

            return self._build_result(request, metrics, "Cleanup completed")

        except TimeoutError:
            logger.exception("Scene cleanup timed out")
            if self._event_emitter:
                try:
                    await self._event_emitter.emit(
                        SceneCleanupFailedEvent(
                            correlation_id=request.correlation_id,
                            success=SuccessFlag(False),
                            mode=request.mode,
                            dry_run=request.dry_run,
                            error_category=SceneErrorCategory.TIMEOUT,
                            message=Prompt(f"[{SceneErrorCategory.TIMEOUT.value}] Cleanup timed out"),
                        )
                    )
                except Exception:
                    logger.warning("Failed to emit SceneCleanupFailedEvent on timeout")
            return self._failure(
                request,
                Prompt(f"[{SceneErrorCategory.TIMEOUT.value}] Cleanup timed out"),
            )
        except ConnectionError:
            logger.exception("Scene cleanup connection failed")
            if self._event_emitter:
                try:
                    await self._event_emitter.emit(
                        SceneCleanupFailedEvent(
                            correlation_id=request.correlation_id,
                            success=SuccessFlag(False),
                            mode=request.mode,
                            dry_run=request.dry_run,
                            error_category=SceneErrorCategory.CONNECTION,
                            message=Prompt(f"[{SceneErrorCategory.CONNECTION.value}] Cleanup connection failed"),
                        )
                    )
                except Exception:
                    logger.warning("Failed to emit SceneCleanupFailedEvent on connection")
            return self._failure(
                request,
                Prompt(f"[{SceneErrorCategory.CONNECTION.value}] Cleanup connection failed"),
            )
        except Exception:
            logger.exception("Scene cleanup failed")
            if self._event_emitter:
                try:
                    await self._event_emitter.emit(
                        SceneCleanupFailedEvent(
                            correlation_id=request.correlation_id,
                            success=SuccessFlag(False),
                            mode=request.mode,
                            dry_run=request.dry_run,
                            error_category=SceneErrorCategory.SCENE_STATE,
                            message=Prompt(f"[{SceneErrorCategory.SCENE_STATE.value}] Scene cleanup failed"),
                        )
                    )
                except Exception:
                    logger.warning("Failed to emit SceneCleanupFailedEvent on generic error")
            return self._failure(
                request,
                Prompt(f"[{SceneErrorCategory.SCENE_STATE.value}] Scene cleanup failed"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    def _pre_flight_check(self, request: SceneCleanupVO) -> SceneError | None:
        """Pre-flight validation — no business logic, just checks."""
        # FR-SCN-002: confirmation required only for destructive operations (not dry-run)
        if not request.dry_run and not request.confirmation and CLEANUP_CONFIRMATION_REQUIRED:
            return SceneError(
                category=SceneErrorCategory.CONFIRMATION,
                message=Prompt("Destructive cleanup requires explicit confirmation"),
            )

        # FR-SCN-002: validate child handling policy
        valid_child_policies = (CHILD_POLICY_DELETE, CHILD_POLICY_DETACH, CHILD_POLICY_REJECT)
        if request.child_handling_policy not in valid_child_policies:
            return SceneError(
                category=SceneErrorCategory.VALIDATION,
                message=Prompt(f"Invalid child handling policy: {request.child_handling_policy}"),
            )

        # FR-SCN-002: validate dependent handling policy
        valid_dependent_policies = (DEPENDENT_POLICY_IGNORE, DEPENDENT_POLICY_REJECT, DEPENDENT_POLICY_REMOVE_SAFE)
        if request.dependent_handling_policy not in valid_dependent_policies:
            return SceneError(
                category=SceneErrorCategory.VALIDATION,
                message=Prompt(f"Invalid dependent handling policy: {request.dependent_handling_policy}"),
            )

        return None

    async def _execute_code(self, code: PythonCode) -> str:
        """Execute code via injected code executor."""
        result = await self._code_executor.execute_blender_code(code)
        output = result.output if hasattr(result, "output") else str(result)
        if not isinstance(output, str):
            raise RuntimeError(f"Expected string output, got {type(output).__name__}")
        return output

    def _build_result(
        self,
        request: SceneCleanupVO,
        metrics: SceneCleanupMetricsVO,
        message: str,
    ) -> SceneCleanupVO:
        """Build success result from parsed metrics."""
        return SceneCleanupVO(
            mode=request.mode,
            preservation_list=request.preservation_list,
            dry_run=request.dry_run,
            confirmation=request.confirmation,
            child_handling_policy=request.child_handling_policy,
            dependent_handling_policy=request.dependent_handling_policy,
            include_hidden_objects=request.include_hidden_objects,
            correlation_id=request.correlation_id,
            success=SuccessFlag(True),
            removed_count=getattr(metrics, "removed_count", ObjectCount(0)),
            preserved_count=getattr(metrics, "preserved_count", ObjectCount(0)),
            skipped_count=getattr(metrics, "skipped_count", ObjectCount(0)),
            removed_object_references=getattr(metrics, "removed_object_references", ()),
            preserved_object_references=getattr(metrics, "preserved_object_references", ()),
            skipped_object_references=getattr(metrics, "skipped_object_references", ()),
            message=Prompt(message),
        )

    def _failure(self, request: SceneCleanupVO, message: Prompt) -> SceneCleanupVO:
        return SceneCleanupVO(
            mode=request.mode,
            preservation_list=request.preservation_list,
            dry_run=request.dry_run,
            confirmation=request.confirmation,
            child_handling_policy=request.child_handling_policy,
            dependent_handling_policy=request.dependent_handling_policy,
            include_hidden_objects=request.include_hidden_objects,
            correlation_id=request.correlation_id,
            success=SuccessFlag(False),
            message=message,
        )

    def __repr__(self) -> str:
        return "SceneCleanupExecutor()"
