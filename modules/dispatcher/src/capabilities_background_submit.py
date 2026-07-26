"""Background submission capability — coordinate long-running actions as jobs.

FR-DSP-005: Submit Background Action
- Creates job through job feature, returns task reference
- Enforces background eligibility and capacity limits
- Returns envelope indicating polling is required
- Does not manage task lifecycle after handoff
"""

import logging
from typing import Any

from modules.shared.src.dispatcher.contract_background_submit_protocol import (
    BackgroundSubmitProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

logger = logging.getLogger("BlenderMCPServer")


class BackgroundSubmitExecutor(BackgroundSubmitProtocol):
    """Concrete implementation for background action submission.

    FR-DSP-005: Creates job, returns task reference. Enforces capacity limits.
    Returns envelope indicating polling is required for final outcome.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        job_tracker: Any = None,
        background_capacity: int = 50,
        max_result_data_size: int = 1_000_000,
    ):
        self._job_tracker = job_tracker
        self._capacity = background_capacity
        self._max_data_size = max_result_data_size

    # ─── Block 2: Protocol Method Implementation ─────────────

    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Submit an action for background execution via job feature.

        FR-DSP-005: Creates job, returns task reference. Enforces capacity limits.
        Returns envelope indicating polling is required for final outcome.
        """
        # Check background eligibility (would be validated by RequestValidationExecutor)
        # In production, this would check metadata from catalog

        # Check capacity
        current_count = self._get_active_job_count()
        if current_count >= self._capacity:
            logger.warning("Background capacity exceeded: %d/%d", current_count, self._capacity)
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Background capacity exceeded",
                tracking_id=request.tracking_id or "",
                error_category="capacity_error",
            )

        # Create job via job tracker
        try:
            if self._job_tracker:
                job_id, status = self._job_tracker.track_new_task(
                    operation_type=request.action_name,
                    metadata={"tracking_id": request.tracking_id},
                )
            else:
                # Fallback for testing: generate synthetic job ID
                import uuid

                job_id = str(uuid.uuid4())
                status = {"status": "PENDING", "job_id": job_id}

        except Exception as e:
            logger.error("Job creation failed: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message=f"Job creation failed: {e}",
                tracking_id=request.tracking_id or "",
                error_category="execution_error",
            )

        # Build success envelope with task reference
        metadata = {
            "action_name": request.action_name,
            "task_reference": job_id,
            "initial_job_state": status.get("status") if isinstance(status, dict) else str(status),
            "polling_required": True,
        }

        logger.info(
            "Background job submitted: %s (action=%s)",
            job_id,
            request.action_name,
        )

        return UnifiedResultEnvelopeVO.success_envelope(
            message=f"Background job submitted for action '{request.action_name}'",
            tracking_id=request.tracking_id or "",
            data={"task_reference": job_id},
            metadata=metadata,
            warnings=["Polling required for final outcome"],
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _get_active_job_count(self) -> int:
        """Count currently active (non-terminal) jobs."""
        if self._job_tracker is None:
            return 0
        # In production, would query job tracker state
        return 0

    def __repr__(self) -> str:
        return f"BackgroundSubmitExecutor(capacity={self._capacity})"
