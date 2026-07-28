"""Job cancel: task cancellation for pending or running tasks.

FR-JOB-003: Cancel a Task
- Only Pending or Running states can be cancelled
- Terminal tasks cannot be cancelled (idempotent: returns current state)
- Stores a sanitized cancellation reason
- Must NOT delete the task record (remains pollable until retention cleanup)

AES Capabilities layer — concrete implementation of `JobCancelProtocol`.

NOTE: FR-JOB-003 requires signalling the executing feature's cancellation hook
for a RUNNING task. That signalling lives in the execution/diagnostics layer,
which is out of scope for this module; the transition itself is applied here
and the aggregate reports the appropriate outcome.
"""

from __future__ import annotations

import logging
import threading

from modules.shared.src.common.taxonomy_core_vo import ErrorString, JobId
from modules.shared.src.job.contract_job_cancel_protocol import JobCancelProtocol
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

from .utility_job_sanitizer import sanitize_error_detail

logger = logging.getLogger("BlenderMCPServer")

_TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}


class JobCancel(JobCancelProtocol):
    """Concrete implementation of the job cancellation protocol."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        jobs_store: dict[str, JobStatus],
        lock: threading.RLock | None = None,
    ) -> None:
        self._jobs = jobs_store
        self._lock = lock or threading.RLock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def cancel_task(self, job_id: JobId, reason: ErrorString = ErrorString("")) -> JobStatus | None:
        """Request cancellation of a pending or running task.

        Returns the resulting status, or None if the task is unknown. For an
        already-terminal task the current status is returned unchanged
        (idempotent). The record is never deleted.
        """
        with self._lock:
            status = self._jobs.get(str(job_id))
            if status is None:
                return None
            if status.status.value in _TERMINAL_STATES:
                # Idempotent: no transition, return current state.
                return status
            sanitized = sanitize_error_detail(str(reason)) or "Cancelled"
            status.mark_cancelled(ErrorString(sanitized))
            logger.info("Task cancelled: %s (reason=%s)", job_id, sanitized)
            return status
