"""Job domain contract: job tracking protocol (ABC based).

Defines the protocol for tracking and updating job lifecycles.
AES Contract layer — pure ABC definitions, no implementation.

FR-JOB-001: Track and Update Task Lifecycle
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    ResultUrl,
)

from .taxonomy_job_status_entity import JobStatus


class JobTrackerProtocol(ABC):
    """Protocol for registering and updating job lifecycles."""

    @abstractmethod
    def track_new_task(self, operation_type: str, metadata: dict | None = None) -> JobId:
        """Register a new background task. Returns unique tracking ID.

        FR-JOB-001: Every task gets a unique, unguessable ID.
        Transitions state from Pending → Running.
        """
        pass

    @abstractmethod
    def update_progress(self, job_id: JobId, progress: float, message: str = "") -> JobStatus:
        """Update progress of a running task (0-100%).

        FR-JOB-001: Progress must be between 0 and 100.
        Returns updated status snapshot.
        """
        pass

    @abstractmethod
    def finalize_task_success(self, job_id: JobId, result_url: ResultUrl | None = None, summary: str = "") -> JobStatus:
        """Mark a task as successfully completed.

        FR-JOB-001: Transitions to Completed state (terminal).
        Optional result reference stored.
        """
        pass

    @abstractmethod
    def finalize_task_failure(self, job_id: JobId, error_message: ErrorString, error_category: str = "") -> JobStatus:
        """Mark a task as failed with error details.

        FR-JOB-001: Transitions to Failed state (terminal).
        Stores sanitized error message and category.
        """
        pass