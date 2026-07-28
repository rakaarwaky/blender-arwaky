"""Capability: Scene cleanup executor.

FR-SCN-002: Cleanup scene objects.

Capabilities layer:
- implements protocol ABC
- 3-block structure
- owns policy resolution
- delegates technical code building/parsing to utility
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import Prompt, PythonCode, SuccessFlag
from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.scene.contract_scene_protocol import ISceneCleanupProtocol
from modules.shared.src.scene.taxonomy_scene_constant import (
    CLEANUP_CONFIRMATION_REQUIRED,
    PRESERVATION_CAMERA,
    PRESERVATION_LIGHT,
    PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA,
    PROTECTED_OBJECT_POLICY_SOLE_CAMERA,
    VALID_CHILD_HANDLING_POLICIES,
    VALID_CLEANUP_MODES,
    VALID_DEPENDENT_HANDLING_POLICIES,
)
from modules.shared.src.scene.taxonomy_scene_error import SceneError, SceneErrorCategory
from modules.shared.src.scene.taxonomy_scene_event import (
    SceneCleanupCompletedEvent,
    SceneCleanupDryRunCompletedEvent,
)
from modules.shared.src.scene.taxonomy_scene_vo import (
    ObjectCount,
    ObjectName,
    SceneCleanupPolicyVO,
    SceneCleanupVO,
)
from modules.shared.src.scene.utility_scene_code_builder import (
    build_cleanup_execution_code,
    build_cleanup_preview_code,
)
from modules.shared.src.scene.utility_scene_result_parser import parse_cleanup_metrics

logger = logging.getLogger("BlenderMCPServer")


class SceneCleanupExecutor(ISceneCleanupProtocol):
    """Capability for FR-SCN-002: scene cleanup."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        if code_executor is None:
            raise ValueError("code_executor must be provided")
        self._code_executor = code_executor

    # ─── Block 2: protocol methods only ───────────────────────
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup or dry-run preview."""
        validation_error = self._validate(request)
        if validation_error is not None:
            return self._failure(request, validation_error.to_prompt())

        if not request.dry_run and not request.confirmation and CLEANUP_CONFIRMATION_REQUIRED:
            confirmation_error = SceneError(
                category=SceneErrorCategory.CONFIRMATION,
                message=Prompt("Destructive cleanup requires explicit confirmation"),
            )
            return self._failure(request, confirmation_error.to_prompt())

        try:
            policy = self._resolve_policy(request)
            code = (
                build_cleanup_preview_code(policy)
                if request.dry_run
                else build_cleanup_execution_code(policy)
            )

            raw = await self._execute_code(code)
            metrics = parse_cleanup_metrics(raw)

            if request.dry_run:
                event = SceneCleanupDryRunCompletedEvent(
                    correlation_id=request.correlation_id,
                    success=SuccessFlag(True),
                    mode=request.mode,
                    removable_count=metrics.removed_count,
                    preserved_count=metrics.preserved_count,
                    skipped_count=metrics.skipped_count,
                    message=Prompt("Scene cleanup dry-run completed"),
                )
                logger.info("scene_cleanup_dry_run_completed event=%s", event.message)

                return self._build_cleanup_result(
                    request,
                    metrics.removed_count,
                    metrics.preserved_count,
                    metrics.skipped_count,
                    metrics.removed_object_references,
                    metrics.preserved_object_references,
                    metrics.skipped_object_references,
                    f"Dry-run cleanup completed: {metrics.removed_count} removable",
                )

            event = SceneCleanupCompletedEvent(
                correlation_id=request.correlation_id,
                success=SuccessFlag(True),
                mode=request.mode,
                removed_count=metrics.removed_count,
                preserved_count=metrics.preserved_count,
                skipped_count=metrics.skipped_count,
                message=Prompt("Scene cleanup completed"),
            )
            logger.info("scene_cleanup_completed event=%s", event.message)

            return self._build_cleanup_result(
                request,
                metrics.removed_count,
                metrics.preserved_count,
                metrics.skipped_count,
                metrics.removed_object_references,
                metrics.preserved_object_references,
                metrics.skipped_object_references,
                f"Cleanup completed: {metrics.removed_count} removed",
            )

        except TimeoutError:
            logger.exception("Scene cleanup timed out")
            return self._failure(
                request,
                Prompt(f"[{SceneErrorCategory.TIMEOUT.value}] Cleanup timed out"),
            )
        except ConnectionError:
            logger.exception("Scene cleanup connection failed")
            return self._failure(
                request,
                Prompt(f"[{SceneErrorCategory.CONNECTION.value}] Cleanup connection failed"),
            )
        except Exception as exc:
            logger.exception("Scene cleanup failed")
            return self._failure(
                request,
                Prompt(f"[{SceneErrorCategory.SCENE_STATE.value}] Cleanup failed: {exc}"),
            )

    # ─── Block 3: dunders / factories / helpers ───────────────
    def _validate(self, request: SceneCleanupVO) -> SceneError | None:
        mode = str(request.mode).lower()

        if mode not in VALID_CLEANUP_MODES:
            return SceneError(
                category=SceneErrorCategory.VALIDATION,
                message=Prompt(f"Invalid cleanup mode: {request.mode}"),
            )

        if request.child_handling_policy not in VALID_CHILD_HANDLING_POLICIES:
            return SceneError(
                category=SceneErrorCategory.VALIDATION,
                message=Prompt(f"Invalid child handling policy: {request.child_handling_policy}"),
            )

        if request.dependent_handling_policy not in VALID_DEPENDENT_HANDLING_POLICIES:
            return SceneError(
                category=SceneErrorCategory.VALIDATION,
                message=Prompt(
                    f"Invalid dependent handling policy: {request.dependent_handling_policy}"
                ),
            )

        return None

    def _resolve_policy(self, request: SceneCleanupVO) -> SceneCleanupPolicyVO:
        preservation = set(request.preservation_list)

        return SceneCleanupPolicyVO(
            mode=request.mode,
            preserve_cameras=PRESERVATION_CAMERA in preservation or PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA,
            preserve_lights=PRESERVATION_LIGHT in preservation,
            include_hidden_objects=request.include_hidden_objects,
            child_handling_policy=request.child_handling_policy,
            dependent_handling_policy=request.dependent_handling_policy,
            protect_active_camera=PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA,
            protect_sole_camera=PROTECTED_OBJECT_POLICY_SOLE_CAMERA,
        )

    async def _execute_code(self, code: PythonCode) -> Prompt:
        result = await self._code_executor.execute_blender_code(code)
        return Prompt(result.output if hasattr(result, 'output') else str(result))

    def _build_cleanup_result(
        self,
        request: SceneCleanupVO,
        removed_count: ObjectCount,
        preserved_count: ObjectCount,
        skipped_count: ObjectCount,
        removed_refs: tuple[ObjectName, ...],
        preserved_refs: tuple[ObjectName, ...],
        skipped_refs: tuple[ObjectName, ...],
        message: str,
    ) -> SceneCleanupVO:
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
            removed_count=removed_count,
            preserved_count=preserved_count,
            skipped_count=skipped_count,
            removed_object_references=removed_refs,
            preserved_object_references=preserved_refs,
            skipped_object_references=skipped_refs,
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
