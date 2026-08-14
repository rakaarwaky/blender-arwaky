"""Reliability acceptance tests at the Job aggregate boundary."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from modules.job.src.agent_job_orchestrator import JobOrchestrator
from modules.job.src.capabilities_job_checker import JobCapacityChecker
from modules.job.src.capabilities_job_evaluator import JobCancellationEvaluator
from modules.job.src.capabilities_job_event_publisher import JobLoggingEventPublisher
from modules.job.src.capabilities_job_monitor import JobStatusMonitor
from modules.job.src.capabilities_job_repository import InMemoryJobLifecycleRepository
from modules.job.src.capabilities_job_resolver import JobCleanupResolver
from modules.shared.src.common.taxonomy_core_vo import Timestamp
from modules.shared.src.job.taxonomy_job_error import CapacityError
from modules.shared.src.job.taxonomy_job_vo import (
    CreateTaskCommand,
    JobPolicy,
    OperationType,
)


def _build_orchestrator(
    *,
    policy: JobPolicy,
    now: float,
) -> tuple[JobOrchestrator, InMemoryJobLifecycleRepository]:
    def clock() -> Timestamp:
        return Timestamp(now)

    lifecycle = InMemoryJobLifecycleRepository(
        policy=policy,
        clock=clock,
        event_publisher=JobLoggingEventPublisher(),
    )
    orchestrator = JobOrchestrator(
        lifecycle=lifecycle,
        monitor=JobStatusMonitor(),
        cancellation=JobCancellationEvaluator(),
        cleanup=JobCleanupResolver(),
        capacity=JobCapacityChecker(),
        policy=policy,
        clock=clock,
    )
    return orchestrator, lifecycle


def test_concurrent_transitions_keep_repository_consistent() -> None:
    """Concurrent starts are serialized without illegal transitions or state loss."""
    policy = JobPolicy(max_active=64)
    _, lifecycle = _build_orchestrator(policy=policy, now=1000.0)
    created = [lifecycle.create_task(CreateTaskCommand(operation_type=OperationType("render"))) for _ in range(32)]

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lifecycle.start_task, (snapshot.job_id for snapshot in created)))

    running = lifecycle.list_running()
    assert len(running) == len(created)
    assert {snapshot.job_id for snapshot in running} == {snapshot.job_id for snapshot in created}
    assert lifecycle.active_count() == len(created)


def test_orchestrator_rejects_capacity_without_partial_record() -> None:
    """Capacity rejection happens before lifecycle creation."""
    policy = JobPolicy(max_active=1)
    orchestrator, lifecycle = _build_orchestrator(policy=policy, now=1000.0)
    first = orchestrator.submit_task(CreateTaskCommand(operation_type=OperationType("render")))

    with pytest.raises(CapacityError):
        orchestrator.submit_task(CreateTaskCommand(operation_type=OperationType("download")))

    assert lifecycle.active_count() == 1
    assert lifecycle.get_record(first.job_id).operation_type == OperationType("render")


def test_orchestrator_cleanup_times_out_stale_running_task() -> None:
    """Cleanup applies stale timeout transition and reclaims capacity."""
    policy = JobPolicy(
        max_active=1,
        stale_recovery_enabled=True,
        stale_running_lifetime_seconds=60.0,
    )
    orchestrator, lifecycle = _build_orchestrator(policy=policy, now=1000.0)
    created = orchestrator.submit_task(CreateTaskCommand(operation_type=OperationType("render")))
    lifecycle.start_task(created.job_id)

    # The fixture clock is intentionally fixed at 1000.0. Move the running
    # timestamp behind the cleanup threshold to exercise the real resolver.
    record = lifecycle._records[str(created.job_id)]
    record.started_at = Timestamp(900.0)
    record.updated_at = Timestamp(900.0)

    summary = orchestrator.cleanup_expired_tasks()

    assert summary.reclaimed_capacity == 1
    assert lifecycle.get_record(created.job_id).state == "TIMED_OUT"
    assert lifecycle.active_count() == 0
