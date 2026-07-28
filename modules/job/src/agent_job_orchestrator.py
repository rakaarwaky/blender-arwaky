"""Agent: Job feature orchestrator.

Coordinates job state tracking, monitoring, cancellation, and cleanup.
Wires capabilities together per FR-JOB requirements.
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    Progress,
    ResultUrl,
)
from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from modules.shared.src.job.taxonomy_job_error import CapacityError
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobOrchestrator(IJobAggregate):
    """Orchestrates job lifecycle operations via capabilities layer."""

    def __init__(self, max_active: int = 100):
        self._jobs: dict[str, JobStatus] = {}
        self._max_active = max_active

    # FR-JOB-001: Track and Update Task Lifecycle

    def track_new_task(self, operation_type: str, _metadata: dict | None = None) -> tuple[JobId, JobStatus]:
        """Register a new background task. Returns unique tracking ID."""
        import uuid

        job_id = JobId(str(uuid.uuid4()))

        # FR-JOB-005: Enforce Background Capacity
        running = sum(1 for j in self._jobs.values() if j.status.value in ("RUNNING", "PENDING"))
        if running >= self._max_active:
            raise CapacityError(max_active=self._max_active, current_active=running)

        status = JobStatus(job_id=job_id)
        self._jobs[str(job_id)] = status
        logger.info("New task tracked: %s (type=%s)", job_id, operation_type)
        return job_id, status

    def update_progress(self, job_id: JobId, progress: float, _message: str = "") -> JobStatus:
        """Update progress of a running task (0-100%)."""
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]
        if progress < 0 or progress > 100:
            raise ValueError(f"Invalid progress value: {progress} (must be 0-100)")
        if status.status.value not in ("RUNNING", "PENDING"):
            raise RuntimeError(f"Cannot update progress on task in {status.status.value} state")

        status.progress = Progress(progress)
        return status

    def finalize_task_success(
        self, job_id: JobId, result_url: ResultUrl | None = None, _summary: str = ""
    ) -> JobStatus:
        """Mark a task as successfully completed."""
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]
        if status.status.value in ("COMPLETED", "FAILED", "CANCELLED"):
            raise RuntimeError(f"Cannot finalize task already in {status.status.value} state")

        status.mark_completed(result_url)
        logger.info("Task completed: %s", job_id)
        return status

    def finalize_task_failure(self, job_id: JobId, error_message: ErrorString, error_category: str = "") -> JobStatus:
        """Mark a task as failed with error details."""
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]
        if status.status.value in ("COMPLETED", "FAILED", "CANCELLED"):
            raise RuntimeError(f"Cannot finalize task already in {status.status.value} state")

        status.mark_failed(error_message)
        logger.info("Task failed: %s (%s)", job_id, error_category)
        return status

    # FR-JOB-002: Monitor Task Status

    def get_task_status(self, job_id: JobId) -> JobStatus | None:
        """Retrieve current state snapshot of a task (read-only)."""
        import copy

        status = self._jobs.get(str(job_id))
        if status is None:
            return None
        return copy.deepcopy(status)

    # FR-JOB-003: Cancel a Task

    def cancel_task(self, job_id: JobId, reason: ErrorString = "") -> tuple[bool, str]:
        """Request cancellation of a waiting or running task."""
        status = self._jobs.get(str(job_id))
        if status is None:
            return False, f"Task {job_id} not found"

        state = status.status.value
        if state in ("COMPLETED", "FAILED", "CANCELLED"):
            return False, f"Cannot cancel task already in {state} state"

        status.mark_cancelled(ErrorString(f"Cancelled: {reason}") if reason else ErrorString("Cancelled"))
        logger.info("Task cancelled: %s (reason=%s)", job_id, reason)
        return True, f"Task {job_id} cancellation accepted"

    # FR-JOB-004: Automatic Task Record Cleanup

    def cleanup_expired_tasks(self, max_retained: int = 100) -> dict[str, int]:
        """Remove old, finished task records."""
        terminal_states = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}

        terminal = [jid for jid, s in self._jobs.items() if s.status.value in terminal_states]
        to_remove = terminal[max_retained:] if len(terminal) > max_retained else []

        for jid in to_remove:
            del self._jobs[jid]

        return {
            "removed": len(to_remove),
            "retained": len(self._jobs) - len(to_remove),
        }
