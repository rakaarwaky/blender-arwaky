"""Background submission capability — coordinate long-running actions as jobs.

FR-DSP-005: Submit Background Action
- Creates job through job feature, returns task reference
- Enforces background eligibility and capacity limits
- Returns envelope indicating polling is required for final outcome
- Does not manage task lifecycle after handoff
"""

import logging

from modules.shared.src.dispatcher.contract_background_submit_protocol import (
    BackgroundSubmitProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO
from modules.shared.src.job.contract_job_aggregate import IJobAggregate

logger = logging.getLogger("BlenderMCPServer")


class BackgroundSubmitExecutor(BackgroundSubmitProtocol):
    """Concrete implementation for background action submission.

    FR-DSP-005: Enforces background eligibility and capacity limits, creates job, returns
    task reference. Returns envelope indicating polling is required for final outcome.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        job_tracker: IJobAggregate | None = None,
        background_capacity: int = 50,
        max_result_data_size: int = 1_000_000,
    ) -> None:
        if job_tracker is None:
            raise ValueError("BackgroundSubmitExecutor requires a real job tracker")
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

        # Create job via real job tracker — no synthetic IDs (FR-DSP-005)
        try:
            snapshot = self._job_tracker.submit_task(
                operation_type=request.action_name,
                correlation_id=tracking_id,
                metadata={"tracking_id": tracking_id},
            )
            job_id = snapshot.job_id
            status_str = str(getattr(snapshot.state, "value", snapshot.state))

        except Exception:
            logger.exception("Background submission failed")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Background submission failed",
                tracking_id=tracking_id,
                error_category="execution_error",
            )

        # Build success envelope with task reference
        metadata = {
            "action_name": request.action_name,
            "task_reference": job_id,
            "initial_job_state": status_str,
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
        """Count currently active (non-terminal) jobs.

        Delegates to the wired job tracker when it exposes an active-count method;
        returns 0 only when no tracker is present. When a tracker is present but
        has no recognized method, logs a warning at higher level and cannot enforce
        capacity.

        Args:
            None (uses self._job_tracker instance attribute).

        Returns:
            Active job count, or 0 when no tracker is configured.
        """
        tracker = self._job_tracker
        if tracker is None:
            return 0
        for method in ("active_job_count", "get_active_count", "count_active_jobs", "active_count"):
            fn: object = getattr(tracker, method, None)
            if callable(fn):
                try:
                    return int(fn())
                except Exception:
                    logger.warning("Job tracker method %s failed", method)
        logger.warning(
            "Job tracker present but no active-count method; "
            "capacity enforcement disabled — ensure job_tracker implements "
            "active_job_count(), get_active_count(), count_active_jobs(), or active_count()"
        )
        return 0

    def __repr__(self) -> str:
        return f"BackgroundSubmitExecutor(capacity={self._capacity})"
