# modules/shared/src/job/contract_job_protocol.py
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import JobId
from .taxonomy_job_vo import (
    CancellationReason,
    CancellationResult,
    CancelTaskCommand,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class IJobRegistry(ABC):
    """Protocol contract for job state management capability."""

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
    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult: ...

    @abstractmethod
    def get_snapshot(self, job_id: JobId) -> JobStatusSnapshot: ...

    @abstractmethod
    def cleanup_expired(self) -> CleanupSummary: ...

    @abstractmethod
    def capacity_status(self) -> CapacityStatus: ...


class ICancellationSignaler(ABC):
    """Protocol contract for signaling job cancellation to the executor."""

    @abstractmethod
    def signal(self, job_id: JobId, reason: CancellationReason | None) -> bool: ...


class IJobEventPublisher(ABC):
    """Protocol contract for publishing job lifecycle events."""

    @abstractmethod
    def publish(self, event: str, payload: Mapping[str, Any]) -> None: ...
