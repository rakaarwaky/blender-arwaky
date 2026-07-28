# modules/shared/src/job/taxonomy_job_error.py
"""Job domain errors."""
from __future__ import annotations

from ..common.taxonomy_core_vo import ErrorString


class JobError(Exception):
    def __init__(self, message: ErrorString | None = None) -> None:
        message = message or ErrorString("Job error")
        super().__init__(message)


class CapacityError(JobError):
    def __init__(self, max_active: int = 100, current_active: int = 100) -> None:
        message = ErrorString(
            f"Background capacity exceeded: {current_active}/{max_active} active tasks"
        )
        super().__init__(message)
        self.max_active = max_active
        self.current_active = current_active


class TaskNotFoundError(JobError):
    def __init__(self, task_id: str) -> None:
        message = ErrorString(f"Task {task_id} not found")
        super().__init__(message)
        self.task_id = task_id


class InvalidStateTransitionError(JobError):
    def __init__(self, from_state: str, to_state: str) -> None:
        message = ErrorString(f"Invalid state transition: {from_state} -> {to_state}")
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state


class ValidationError(JobError):
    def __init__(self, message: ErrorString) -> None:
        super().__init__(message)