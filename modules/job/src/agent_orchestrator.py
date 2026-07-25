"""Agent: Job feature orchestrator.

Coordinates job state tracking and progress reporting.
"""

import logging
from typing import Any

from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobOrchestrator:
    """Orchestrates job lifecycle operations."""

    def __init__(self):
        self._jobs: dict[str, JobStatus] = {}

    def create_job(self, job_id: str) -> JobStatus:
        """Create a new job."""
        status = JobStatus(job_id=job_id)
        self._jobs[job_id] = status
        return status

    def get_job(self, job_id: str) -> JobStatus | None:
        """Get job status."""
        return self._jobs.get(job_id)

    def update_progress(self, job_id: str, progress: int) -> None:
        """Update job progress."""
        if job_id in self._jobs:
            self._jobs[job_id].progress = progress
