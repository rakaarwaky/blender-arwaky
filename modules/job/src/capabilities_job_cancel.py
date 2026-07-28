"""Job cancel: task cancellation for waiting or running tasks.

FR-JOB-003: Cancel a Task
- Only Pending or Running states can be cancelled
- Finished tasks cannot be cancelled
- Stores cancellation reason
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import ErrorString, JobId
from modules.shared.src.job.contract_job_cancel_protocol import JobCancelProtocol
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobCancel:
    """Business logic for requesting task cancellation."""

    def __init__(self, jobs_store: dict[str, JobStatus]):
        self._jobs = jobs_store

    def cancel_task(self, job_id: JobId, reason: ErrorString = "") -> tuple[bool, str]:
        """Request cancellation of a waiting or running task.

        FR-JOB-003: Only allowed for Pending or Running states.
        Returns (success, message) tuple.
        """
        status = self._jobs.get(str(job_id))
        if status is None:
            return False, f"Task {job_id} not found"

        state = status.status.value

        # Only Pending or Running tasks can be cancelled
        if state == "COMPLETED":
            return False, "Cannot cancel task already completed"
        if state == "FAILED":
            return False, "Cannot cancel task already failed"
        if state == "CANCELLED":
            return False, "Task already cancelled"

        # Transition to Cancelled
        status.mark_cancelled(ErrorString(f"Cancelled: {reason}") if reason else ErrorString("Cancelled"))

        logger.info("Task cancelled: %s (reason=%s)", job_id, reason)
        return True, f"Task {job_id} cancellation accepted"
