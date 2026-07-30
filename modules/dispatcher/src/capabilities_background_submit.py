"""Background submission capability — coordinate long-running actions as jobs.

FR-DSP-005: Submit Background Action
- Creates job through job feature, returns task reference
- Enforces background eligibility and capacity limits
- Returns envelope indicating polling is required for final outcome
- Does not manage task lifecycle after handoff
"""

from __future__ import annotations

import logging

from modules.shared.src.dispatcher.contract_background_submit_protocol import (
    BackgroundSubmitProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import (
    UnifiedResultEnvelopeVO,
)
from modules.shared.src.job.contract_job_lifecycle_protocol import IJobLifecycle
from modules.shared.src.job.taxonomy_job_vo import (
    CreateTaskCommand,
    OperationType,
    TaskMetadata,
)

logger = logging.getLogger("BlenderMCPServer")


class BackgroundSubmitExecutor(BackgroundSubmitProtocol):
    """Concrete implementation for background action submission.

    FR-DSP-005: Enforces background eligibility and capacity limits, creates job, returns
    task reference. Returns envelope indicating polling is required for final outcome.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        job_tracker: IJobLifecycle,
        background_capacity: int = 50,
        max_result_data_size: int = 1_000_000,
    ):
        self._job_tracker = job_tracker
        self._capacity = background_capacity
        self._max_data_size = max_result_data_size

    # ─── Block 2: Protocol Method Implementation ─────────────

    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Submit an action for background execution via job feature.

        FR-DSP-005: Enforces eligibility and capacity, creates job, returns task reference.
        Returns envelope indicating polling is required for final outcome.
        """
        tracking_id = request.validated_tracking_id or request.tracking_id or ""

        # Background eligibility (FR-DSP-005)
        bg_eligible = request.resolved_metadata.get("background_eligibility_flag", False)
        if not bg_eligible:
            logger.warning(
                "Action '%s' is not eligible for background execution", request.action_name
            )
            return UnifiedResultEnvelopeVO.error_envelope(
                message=f"Action '{request.action_name}' does not support background execution",
                tracking_id=tracking_id,
                error_category="unsupported_error",
            )

        # Capacity enforcement (FR-DSP-005)
        current_count = self._get_active_job_count()
        if current_count >= self._capacity:
            logger.warning("Background capacity exceeded: %d/%d", current_count, self._capacity)
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Background capacity exceeded",
                tracking_id=tracking_id,
                error_category="capacity_error",
            )

        # Create job via job feature (FR-DSP-005: atomic submission)
        try:
            command = CreateTaskCommand(
                operation_type=OperationType(request.action_name),
                metadata=TaskMetadata({"tracking_id": tracking_id}),
            )
            snapshot = self._job_tracker.create_task(command)
            job_id = str(snapshot.job_id)
            status = str(snapshot.state.value)
        except Exception as e:
            logger.error("Job creation failed: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Job creation failed",
                tracking_id=tracking_id,
                error_category="execution_error",
            )

        # Build success envelope with task reference
        metadata = {
            "action_name": request.action_name,
            "task_reference": job_id,
            "initial_job_state": status,
            "polling_required": True,
        }

        logger.info(
            "Background job submitted: %s (action=%s)",
            job_id,
            request.action_name,
        )

        return UnifiedResultEnvelopeVO.success_envelope(
            message=f"Background job submitted for action '{request.action_name}'",
            tracking_id=tracking_id,
            data={"task_reference": job_id},
            metadata=metadata,
            warnings=["Polling required for final outcome"],
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _get_active_job_count(self) -> int:
        return self._job_tracker.active_count()

    def __repr__(self) -> str:
        return f"BackgroundSubmitExecutor(capacity={self._capacity})"
