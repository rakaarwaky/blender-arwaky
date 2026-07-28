"""Job monitor: read-only task status retrieval.

FR-JOB-002: Monitor Task Status
- Read-only snapshot of task state, progress, timestamps, results
- Consistent under concurrency via a shared lock + deep copy
- Not-found handling for expired/cleaned up tasks

AES Capabilities layer — concrete implementation of `JobMonitorProtocol`.
"""

from __future__ import annotations

import copy
import logging
import threading

from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.job.contract_job_monitor_protocol import JobMonitorProtocol
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobMonitor(JobMonitorProtocol):
    """Concrete implementation of the job monitoring protocol."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        jobs_store: dict[str, JobStatus],
        lock: threading.RLock | None = None,
    ) -> None:
        self._jobs = jobs_store
        self._lock = lock or threading.RLock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def get_task_status(self, job_id: JobId) -> JobStatus | None:
        """Retrieve a consistent, read-only snapshot of a task.

        FR-JOB-002: never mutates task state. Returns a deep copy taken under
        the shared lock so concurrent transitions cannot produce a partial view.
        Returns None if the task is unknown or already purged.
        """
        with self._lock:
            status = self._jobs.get(str(job_id))
            if status is None:
                logger.debug("Task %s not found", job_id)
                return None
            return copy.deepcopy(status)
