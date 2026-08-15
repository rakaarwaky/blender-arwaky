from __future__ import annotations

from modules.job.src.root_job_container import create_job_feature
from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.job.taxonomy_job_vo import CancelTaskCommand, CreateTaskCommand, OperationType


def test_job_status_and_cancel_are_visible_across_containers(tmp_path) -> None:
    store = tmp_path / "jobs.json"
    first = create_job_feature(storage_path=store)
    created = first.submit_task(CreateTaskCommand(operation_type=OperationType("render")))

    second = create_job_feature(storage_path=store)
    observed = second.get_task_status(JobId(str(created.job_id)))
    assert observed.job_id == created.job_id  # nosec B101
    assert observed.state == created.state  # nosec B101

    cancelled = second.cancel_task(CancelTaskCommand(job_id=JobId(str(created.job_id))))
    assert cancelled.accepted is True  # nosec B101

    third = create_job_feature(storage_path=store)
    final = third.get_task_status(JobId(str(created.job_id)))
    assert str(final.state) == "CANCELLED"  # nosec B101
    assert store.exists()  # nosec B101
    assert not list(tmp_path.glob("*.tmp"))  # nosec B101
