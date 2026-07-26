"""Job domain contract: job monitoring protocol (ABC based).

Defines the protocol for monitoring task status and retrieving snapshots.
AES Contract layer — pure ABC definitions, no implementation.

FR-JOB-002: Monitor Task Status
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import JobId

from .taxonomy_job_status_entity import JobStatus


class JobMonitorProtocol(ABC):
    """Protocol for retrieving read-only task status snapshots."""

    @abstractmethod
    def get_task_status(self, job_id: JobId) -> JobStatus | None:
        """Retrieve current state snapshot of a task.

        FR-JOB-002: Strictly read-only, never alters task state.
        Returns consistent snapshot with state, progress, timestamps, and results.
        Returns None if task not found or cleaned up.
        """
        pass
