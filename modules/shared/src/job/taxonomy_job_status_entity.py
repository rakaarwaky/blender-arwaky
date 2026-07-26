"""Mutable job status tracking entity."""

from __future__ import annotations

from ..common.taxonomy_core_vo import ErrorString, JobId, JobState, Progress, ResultUrl
from .taxonomy_job_state_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
)


class JobStatus:
    """Mutable tracking of an async background job."""

    def __init__(
        self,
        job_id: JobId,
        status: JobState = JOB_STATE_PENDING,
        progress: Progress | None = None,
        result_url: ResultUrl | None = None,
        error: ErrorString | None = None,
    ) -> None:
        self.job_id = job_id
        self.status: JobState = status
        self.progress: Progress = progress if progress is not None else Progress(0.0)
        self.result_url: ResultUrl | None = result_url
        self.error: ErrorString | None = error

    def mark_running(self) -> None:
        """Transition to running state."""
        self.status = JOB_STATE_RUNNING
        self.progress = Progress(0.0)

    def mark_completed(self, result_url: ResultUrl | None = None) -> None:
        """Transition to completed state."""
        self.status = JOB_STATE_COMPLETED
        self.progress = Progress(100.0)
        self.result_url = result_url

    def mark_failed(self, error: ErrorString) -> None:
        """Transition to failed state."""
        self.status = JOB_STATE_FAILED
        self.error = error

    def mark_cancelled(self, reason: ErrorString | None = None) -> None:
        """Transition to cancelled state."""
        self.status = JOB_STATE_CANCELLED
        if reason:
            self.error = reason

    def mark_timed_out(self) -> None:
        """Transition to timed out state."""
        self.status = JOB_STATE_TIMED_OUT


def create_job_id(raw: str) -> JobId:
    """Factory helper to create a JobId from a raw string."""
    return JobId(raw)


def create_progress(raw: float) -> Progress:
    """Factory helper to create a validated Progress value."""
    if raw < 0.0 or raw > 100.0:
        raise ValueError("progress must be between 0.0 and 100.0")
    return Progress(raw)