"""Job domain — FR-JOB-001: Track and update task lifecycle."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import JobId
from .taxonomy_job_vo import (
    ActiveCount,
    CancellationReason,
    CompleteTaskCommand,
    CreateTaskCommand,
    DeletedCount,
    FailTaskCommand,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class IJobLifecycle(ABC):
    @abstractmethod
    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def start_task(self, job_id: JobId) -> JobStatusSnapshot: ...
    @abstractmethod
    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def apply_cancel(self, job_id: JobId, reason: CancellationReason | None) -> JobStatusSnapshot: ...
    @abstractmethod
    def apply_timeout(self, job_id: JobId) -> JobStatusSnapshot: ...
    @abstractmethod
    def get_record(self, job_id: JobId) -> JobStatusSnapshot: ...
    @abstractmethod
    def list_terminal(self) -> tuple[JobStatusSnapshot, ...]: ...
    @abstractmethod
    def list_running(self) -> tuple[JobStatusSnapshot, ...]: ...
    @abstractmethod
    def delete_records(self, job_ids: tuple[JobId, ...]) -> DeletedCount: ...
    @abstractmethod
    def active_count(self) -> ActiveCount: ...
