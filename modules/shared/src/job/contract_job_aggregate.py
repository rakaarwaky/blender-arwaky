# modules/shared/src/job/contract_job_aggregate.py
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import JobId
from .taxonomy_job_vo import (
    CancelTaskCommand,
    CancellationResult,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class IJobAggregate(ABC):
    @abstractmethod
    def submit_task(self, command: CreateTaskCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def start_task(self, job_id: JobId) -> JobStatusSnapshot: ...

    @abstractmethod
    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult: ...

    @abstractmethod
    def get_task_status(self, job_id: JobId) -> JobStatusSnapshot: ...

    @abstractmethod
    def cleanup_expired_tasks(self) -> CleanupSummary: ...

    @abstractmethod
    def get_capacity_status(self) -> CapacityStatus: ...
