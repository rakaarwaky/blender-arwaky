# modules/shared/src/job/contract_job_protocol.py
"""Job domain protocols — 5 protocols, one per FR."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import JobId, JobState, Timestamp
from .taxonomy_job_vo import (
    CancelTaskCommand,
    CancellationReason,
    CancellationResult,
    CapacityDecision,
    CleanupDecision,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobPolicy,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


# ─── FR-JOB-001 ──────────────────────────────────────────────────────────────

class IJobLifecycle(ABC):
    """Track and update task lifecycle."""

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
    def delete_records(self, job_ids: tuple[JobId, ...]) -> int: ...

    @abstractmethod
    def active_count(self) -> int: ...


# ─── FR-JOB-002 ──────────────────────────────────────────────────────────────

class IJobMonitor(ABC):
    """Monitor task status — project safe read models."""

    @abstractmethod
    def project(self, snapshot: JobStatusSnapshot) -> JobStatusSnapshot: ...


# ─── FR-JOB-003 ──────────────────────────────────────────────────────────────

class IJobCancellation(ABC):
    """Cancel a task — evaluate cancellation eligibility."""

    @abstractmethod
    def evaluate(self, command: CancelTaskCommand, current_state: JobState) -> CancellationResult: ...


# ─── FR-JOB-004 ──────────────────────────────────────────────────────────────

class IJobCleanup(ABC):
    """Automatic task record cleanup — resolve purge decisions."""

    @abstractmethod
    def resolve(
        self,
        terminal: tuple[JobStatusSnapshot, ...],
        running: tuple[JobStatusSnapshot, ...],
        now: Timestamp,
        policy: JobPolicy,
    ) -> CleanupDecision: ...


# ─── FR-JOB-005 ──────────────────────────────────────────────────────────────

class IJobCapacity(ABC):
    """Enforce background capacity — evaluate submission eligibility."""

    @abstractmethod
    def evaluate(self, active_count: int, policy: JobPolicy) -> CapacityDecision: ...
