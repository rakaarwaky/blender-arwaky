"""Job domain contract: job cancellation protocol (ABC based).

Defines the protocol for cancelling waiting or running tasks.
AES Contract layer — pure ABC definitions, no implementation.

FR-JOB-003: Cancel a Task
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ErrorString, JobId

from .taxonomy_job_status_entity import JobStatus


class JobCancelProtocol(ABC):
    """Protocol for requesting task cancellation."""

    @abstractmethod
    def cancel_task(self, job_id: JobId, reason: ErrorString = "") -> JobStatus | None:
        """Request cancellation of a waiting or running task.

        FR-JOB-003: Only allowed for Pending or Running states.
        Finished tasks cannot be cancelled.
        Returns updated status or None if not found.
        """
        pass