from __future__ import annotations

from dataclasses import dataclass

from modules.cli.src.surface_cli_action_router import CliActionRouter


@dataclass(frozen=True)
class FakeSnapshot:
    job_id: str
    state: str


@dataclass(frozen=True)
class FakeCapacity:
    active: int
    limit: int
    available: int


class FakeJob:
    def __init__(self) -> None:
        self.submissions: list[object] = []

    def submit_task(self, command: object) -> FakeSnapshot:
        self.submissions.append(command)
        return FakeSnapshot(job_id="task-001", state="PENDING")

    def list_tasks(self) -> tuple[FakeSnapshot, ...]:
        return (FakeSnapshot(job_id="task-001", state="RUNNING"),)

    def get_capacity_status(self) -> FakeCapacity:
        return FakeCapacity(active=1, limit=4, available=3)


def _router_with_job(job: FakeJob) -> CliActionRouter:
    router = object.__new__(CliActionRouter)
    router._job = job
    return router


def test_submit_task_uses_typed_command() -> None:
    job = FakeJob()
    router = _router_with_job(job)

    result = router.execute_action(
        "submit_task",
        {"operation_type": "render", "correlation_id": "corr-1", "metadata": {"scene": "demo"}},
    )

    assert result == {"job_id": "task-001", "state": "PENDING"}  # nosec B101
    command = job.submissions[0]
    assert command.operation_type == "render"  # nosec B101
    assert command.correlation_id == "corr-1"  # nosec B101
    assert command.metadata == {"scene": "demo"}  # nosec B101


def test_list_tasks_returns_shared_job_snapshots() -> None:
    router = _router_with_job(FakeJob())

    assert router.execute_action("list_tasks", {}) == {
        "tasks": [{"job_id": "task-001", "state": "RUNNING"}],
        "count": 1,
    }  # nosec B101


def test_get_capacity_status_returns_shared_capacity() -> None:
    router = _router_with_job(FakeJob())

    assert router.execute_action("get_capacity_status", {}) == {
        "active": 1,
        "limit": 4,
        "available": 3,
    }  # nosec B101
