# modules/shared/src/job/taxonomy_job_error.py
"""Job domain errors."""
from __future__ import annotations

from ..common.taxonomy_core_vo import ErrorString, JobId, JobState
from .taxonomy_job_vo import ActiveCount


class JobError(Exception):
    """Base error for job domain operations."""

    def __init__(self, message: ErrorString | None = None) -> None:
        message = message or ErrorString("Job error")
        super().__init__(message)


class CapacityError(JobError):
    """Raised when background capacity is exceeded."""

    def __init__(self, max_active: ActiveCount, current_active: ActiveCount) -> None:
        message = ErrorString(
            f"Background capacity exceeded: {current_active}/{max_active} active tasks"
        )
        super().__init__(message)
        self.max_active = max_active
        self.current_active = current_active


class TaskNotFoundError(JobError):
    """Raised when a requested task ID is not found."""

    def __init__(self, task_id: JobId) -> None:
        message = ErrorString(f"Task {task_id} not found")
        super().__init__(message)
        self.task_id = task_id


class InvalidStateTransitionError(JobError):
    """Raised when a state transition is not allowed."""

    def __init__(self, from_state: JobState, to_state: JobState) -> None:
        message = ErrorString(f"Invalid state transition: {from_state} -> {to_state}")
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state


class JobValidationError(JobError):
    """Raised when job validation fails."""

    def __init__(self, message: ErrorString) -> None:
        super().__init__(message)


class RecordNotFoundError(JobError):
    """Raised when a requested record ID is not found."""

    def __init__(self, record_id: JobId) -> None:
        message = ErrorString(f"Record {record_id} not found")
        super().__init__(message)
        self.record_id = record_id


class RecordCountError(JobError):
    """Raised when record count exceeds limits."""

    def __init__(self, max_records: ActiveCount, current_records: ActiveCount) -> None:
        message = ErrorString(
            f"Record count exceeded: {current_records}/{max_records} records"
        )
        super().__init__(message)
        self.max_records = max_records
        self.current_records = current_records


# ─── Backward-compatible aliases ────────────────────────────────

ValidationError = JobValidationError

