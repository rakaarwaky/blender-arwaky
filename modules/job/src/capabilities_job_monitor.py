"""Job monitor: read-only task status retrieval.

FR-JOB-002: Monitor Task Status
- Read-only snapshot of task state, progress, timestamps, results
- Automatic redaction of sensitive metadata
- Not found handling for expired/cleaned up tasks
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobMonitor:
    """Business logic for monitoring task status snapshots."""

    def __init__(self, jobs_store: dict[str, JobStatus]):
        self._jobs = jobs_store

    def get_task_status(self, job_id: JobId) -> JobStatus | None:
        """Retrieve current state snapshot of a task.

        FR-JOB-002: Strictly read-only, never alters task state.
        Returns consistent snapshot with state, progress, timestamps, and results.
        Returns None if task not found or cleaned up.
        """
        status = self._jobs.get(str(job_id))
        if status is None:
            logger.debug("Task %s not found", job_id)
            return None

        # Return a copy to ensure read-only semantics
        import copy
        return copy.deepcopy(status)
