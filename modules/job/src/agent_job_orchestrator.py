# modules/job/src/agent_job_orchestrator.py
from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from modules.shared.src.job.contract_job_protocol import IJobRegistry
from modules.shared.src.job.taxonomy_job_vo import (
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


class JobOrchestrator(IJobAggregate):
    """
    Thin agent facade.

    This orchestrator delegates to capability contracts and does not
    contain business logic or state.
    """

    def __init__(self, registry: IJobRegistry) -> None:
        self._registry = registry

    def submit_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        return self._registry.create_task(command)

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        return self._registry.start_task(job_id)

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        return self._registry.update_progress(command)

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        return self._registry.complete_task(command)

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        return self._registry.fail_task(command)

    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult:
        return self._registry.cancel_task(command)

    def get_task_status(self, job_id: JobId) -> JobStatusSnapshot:
        return self._registry.get_snapshot(job_id)

    def cleanup_expired_tasks(self) -> CleanupSummary:
        return self._registry.cleanup_expired()

    def get_capacity_status(self) -> CapacityStatus:
        return self._registry.capacity_status()
