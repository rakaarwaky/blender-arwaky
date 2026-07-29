# modules/job/src/agent_job_orchestrator.py
"""Agent: Job feature orchestrator.

Composes 5 capabilities into executable flows.
Controls sequence and movement, not business calculation.
"""
from __future__ import annotations

import time

from modules.shared.src.common.taxonomy_core_vo import JobId, Timestamp
from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from modules.shared.src.job.contract_job_cancellation_protocol import IJobCancellation
from modules.shared.src.job.contract_job_capacity_protocol import IJobCapacity
from modules.shared.src.job.contract_job_cleanup_protocol import IJobCleanup
from modules.shared.src.job.contract_job_lifecycle_protocol import IJobLifecycle
from modules.shared.src.job.contract_job_monitor_protocol import IJobMonitor
from modules.shared.src.job.taxonomy_job_constant import (
    CANCELLATION_ALREADY_TERMINAL,
    CANCELLATION_NOT_FOUND,
)
from modules.shared.src.job.taxonomy_job_error import (
    CapacityError,
    InvalidStateTransitionError,
    TaskNotFoundError,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancelTaskCommand,
    CancellationResult,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobPolicy,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class JobOrchestrator(IJobAggregate):
    """Thin agent facade composing 5 job capabilities."""

    def __init__(
        self,
        lifecycle: IJobLifecycle,
        monitor: IJobMonitor,
        cancellation: IJobCancellation,
        cleanup: IJobCleanup,
        capacity: IJobCapacity,
        policy: JobPolicy,
    ) -> None:
        self._lifecycle = lifecycle
        self._monitor = monitor
        self._cancellation = cancellation
        self._cleanup = cleanup
        self._capacity = capacity
        self._policy = policy

    def submit_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        active = self._lifecycle.active_count()
        decision = self._capacity.evaluate(active, self._policy)
        if not decision.accepted:
            raise CapacityError(max_active=decision.limit, current_active=decision.active)
        return self._lifecycle.create_task(command)

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        return self._lifecycle.start_task(job_id)

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        return self._lifecycle.update_progress(command)

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        return self._lifecycle.complete_task(command)

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        return self._lifecycle.fail_task(command)

    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult:
        try:
            snapshot = self._lifecycle.get_record(command.job_id)
        except TaskNotFoundError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_NOT_FOUND,
                message="Task not found",
            )

        decision = self._cancellation.evaluate(command, snapshot.state)
        if not decision.accepted:
            return decision

        try:
            self._lifecycle.apply_cancel(command.job_id, command.reason)
        except TaskNotFoundError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_NOT_FOUND,
                message="Task not found",
            )
        except InvalidStateTransitionError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_ALREADY_TERMINAL,
                message="Task reached terminal state before cancellation applied",
            )

        return decision

    def get_task_status(self, job_id: JobId) -> JobStatusSnapshot:
        raw = self._lifecycle.get_record(job_id)
        return self._monitor.project(raw)

    def cleanup_expired_tasks(self) -> CleanupSummary:
        now = Timestamp(time.time())
        terminal = self._lifecycle.list_terminal()
        running = self._lifecycle.list_running()

        decision = self._cleanup.resolve(terminal, running, now, self._policy)

        reclaimed = 0
        for job_id in decision.stale_timeout_ids:
            try:
                self._lifecycle.apply_timeout(job_id)
                reclaimed += 1
            except (TaskNotFoundError, InvalidStateTransitionError):
                pass

        purged = self._lifecycle.delete_records(decision.purge_ids)

        return CleanupSummary(
            purged=purged,
            retained=len(terminal) - purged + self._lifecycle.active_count(),
            reclaimed_capacity=reclaimed,
            warnings=decision.warnings,
        )

    def get_capacity_status(self) -> CapacityStatus:
        active = self._lifecycle.active_count()
        decision = self._capacity.evaluate(active, self._policy)
        return CapacityStatus(
            active=decision.active,
            limit=decision.limit,
            available=decision.available,
        )
