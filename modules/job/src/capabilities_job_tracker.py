"""Job tracker: task lifecycle tracking and progress updates.

FR-JOB-001: Track and Update Task Lifecycle
- Unique unguessable tracking IDs (UUID4)
- Forward-only lifecycle: Pending → Running → Completed / Failed / Cancelled
- Progress 0-100, monotonic, bounded
- Terminal-state immutability

AES Capabilities layer — concrete implementation of `JobTrackerProtocol`.
Capacity enforcement is intentionally NOT performed here; it is the
responsibility of the aggregate (`JobOrchestrator`) via `JobCapacityEnforcer`,
so the single authority on concurrency lives in one place (FR-JOB-005).
"""

from __future__ import annotations

import logging
import threading
import uuid

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    Progress,
    ResultUrl,
)
from modules.shared.src.job.contract_job_tracker_protocol import JobTrackerProtocol
from modules.shared.src.job.taxonomy_job_state_constant import (
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
)
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

from .taxonomy_job_error import JobNotFoundError, JobStateError, JobValidationError
from .utility_job_sanitizer import sanitize_error_detail

logger = logging.getLogger("BlenderMCPServer")

_ACTIVE_STATES = (JOB_STATE_PENDING, JOB_STATE_RUNNING)
_TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}


class JobTracker(JobTrackerProtocol):
    """Concrete implementation of the job tracking protocol.

    Owns the in-memory task registry for the job feature. All mutations are
    guarded by the shared lock so transitions stay atomic and thread-safe
    (FR-JOB-001).
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        jobs_store: dict[str, JobStatus],
        max_active: int = 100,
        lock: threading.RLock | None = None,
    ) -> None:
        self._jobs = jobs_store
        self._max_active = max_active
        self._lock = lock or threading.RLock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def track_new_task(
        self, operation_type: str, metadata: dict | None = None
    ) -> tuple[JobId, JobStatus]:
        """Register a new background task with a unique ID.

        FR-JOB-001: generates an unguessable UUID4, starts in PENDING, records
        the creation timestamp (see note). Returns ``(job_id, status)`` to keep
        the historical two-tuple contract used by callers such as the
        dispatcher background-submit capability.
        """
        job_id = JobId(str(uuid.uuid4()))
        with self._lock:
            status = JobStatus(job_id=job_id)
            self._jobs[str(job_id)] = status
        logger.info("New task tracked: %s (type=%s, total=%d)", job_id, operation_type, len(self._jobs))
        return job_id, status

    def update_progress(self, job_id: JobId, progress: float, message: str = "") -> JobStatus:
        """Update progress of a running task (0-100%), monotonic by default.

        FR-JOB-001/002: validates range, rejects non-active states, and refuses
        to move progress backward (monotonic). ``message`` is accepted for API
        symmetry but is not persisted (no message field on the entity).
        """
        if progress < 0 or progress > 100:
            raise JobValidationError(f"Invalid progress value: {progress} (must be 0-100)")
        with self._lock:
            status = self._require(job_id)
            if status.status not in _ACTIVE_STATES:
                raise JobStateError(
                    f"Cannot update progress on task in {status.status.value} state"
                )
            if progress < status.progress:
                raise JobValidationError(
                    f"Progress must be monotonic: {progress} < current {status.progress.value}"
                )
            status.progress = Progress(progress)
            return status

    def finalize_task_success(
        self, job_id: JobId, result_url: ResultUrl | None = None, summary: str = ""
    ) -> JobStatus:
        """Mark a task completed (terminal). FR-JOB-001."""
        with self._lock:
            status = self._require(job_id)
            self._ensure_runnable(status)
            status.mark_completed(result_url)
            logger.info("Task completed: %s", job_id)
            return status

    def finalize_task_failure(
        self, job_id: JobId, error_message: ErrorString, error_category: str = ""
    ) -> JobStatus:
        """Mark a task failed (terminal) with sanitized error detail. FR-JOB-001."""
        with self._lock:
            status = self._require(job_id)
            self._ensure_runnable(status)
            sanitized = ErrorString(sanitize_error_detail(str(error_message)))
            status.mark_failed(sanitized)
            logger.info("Task failed: %s (%s)", job_id, error_category)
            return status

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _require(self, job_id: JobId) -> JobStatus:
        status = self._jobs.get(str(job_id))
        if status is None:
            raise JobNotFoundError(f"Task {job_id} not found")
        return status

    @staticmethod
    def _ensure_runnable(status: JobStatus) -> None:
        if status.status.value in _TERMINAL_STATES:
            raise JobStateError(
                f"Cannot finalize task already in {status.status.value} state"
            )


# Backwards-compatible re-export for any legacy import path.
StateError = JobStateError
