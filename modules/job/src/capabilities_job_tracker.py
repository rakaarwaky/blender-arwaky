"""Job tracker: task lifecycle tracking and progress updates.

FR-JOB-001: Track and Update Task Lifecycle
- Unique unguessable tracking IDs (UUID4)
- Forward-only lifecycle: Pending → Running → Completed / Failed / Cancelled
- Progress 0-100, monotonically increasing
- Maximum active task limit enforcement
"""

import logging
import uuid
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    Progress,
    ResultUrl,
)
from modules.shared.src.job.contract_job_tracker_protocol import (
    JobTrackerProtocol,
)
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobTracker:
    """Business logic for tracking job lifecycles and progress."""

    def __init__(self, max_active: int = 100):
        self._jobs: dict[str, JobStatus] = {}
        self._max_active = max_active

    def track_new_task(self, operation_type: str, metadata: dict | None = None) -> tuple[JobId, JobStatus]:
        """Register a new background task with unique ID.

        FR-JOB-001: Generates unguessable UUID4 tracking ID.
        Transitions state from Pending → Running.
        Enforces maximum active task limit.
        """
        # Check capacity
        running = sum(1 for j in self._jobs.values() if j.status.value in ("RUNNING", "PENDING"))
        if running >= self._max_active:
            raise OverflowError(f"Maximum active tasks ({self._max_active}) reached")

        job_id = JobId(str(uuid.uuid4()))
        status = JobStatus(job_id=job_id)
        self._jobs[str(job_id)] = status
        logger.info("New task tracked: %s (type=%s, total=%d)", job_id, operation_type, len(self._jobs))
        return job_id, status

    def update_progress(self, job_id: JobId, progress: float, message: str = "") -> JobStatus:
        """Update progress of a running task (0-100%).

        FR-JOB-001: Validates progress range. Returns updated status snapshot.
        """
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]

        # Validate progress range
        if progress < 0 or progress > 100:
            raise ValueError(f"Invalid progress value: {progress} (must be 0-100)")

        # Only Running tasks can have progress updates
        if status.status.value not in ("RUNNING", "PENDING"):
            raise StateError(f"Cannot update progress on task in {status.status.value} state")

        status.progress = Progress(progress)
        return status

    def finalize_task_success(self, job_id: JobId, result_url: ResultUrl | None = None, summary: str = "") -> JobStatus:
        """Mark a task as successfully completed.

        FR-JOB-001: Transitions to Completed state (terminal).
        """
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]

        if status.status.value in ("COMPLETED", "FAILED", "CANCELLED"):
            raise StateError(f"Cannot finalize task already in {status.status.value} state")

        status.mark_completed(result_url)
        logger.info("Task completed: %s", job_id)
        return status

    def finalize_task_failure(self, job_id: JobId, error_message: ErrorString, error_category: str = "") -> JobStatus:
        """Mark a task as failed with error details.

        FR-JOB-001: Transitions to Failed state (terminal).
        Stores sanitized error message and category.
        """
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]

        if status.status.value in ("COMPLETED", "FAILED", "CANCELLED"):
            raise StateError(f"Cannot finalize task already in {status.status.value} state")

        status.mark_failed(error_message)
        logger.info("Task failed: %s (%s)", job_id, error_category)
        return status


class StateError(Exception):
    """Error raised when an invalid state transition is attempted."""

    pass
