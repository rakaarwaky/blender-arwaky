"""Utility: Job state transition logic — stateless standalone functions.

Encapsulates transition validation, state mutation, and capacity tracking.
Moved from capabilities layer to shared utility per AES201 compliance.
"""
from __future__ import annotations

import uuid
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    Timestamp,
)
from modules.shared.src.job.taxonomy_job_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    TERMINAL_JOB_STATES,
    VALID_JOB_TRANSITIONS,
)
from modules.shared.src.job.taxonomy_job_entity import JobRecord
from modules.shared.src.job.taxonomy_job_error import (
    InvalidStateTransitionError,
    TaskNotFoundError,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    ErrorCategory,
    JobPolicy,
    JobStatusSnapshot,
    ProgressMessage,
    ResultUrl,
)


def validate_transition(current: JobState, target: JobState) -> None:
    """Validate that a state transition is allowed.

    Raises InvalidStateTransitionError if the transition is not permitted.
    """
    allowed = VALID_JOB_TRANSITIONS.get(current, frozenset())
    if target not in allowed:
        raise InvalidStateTransitionError(str(current), str(target))


def _counts_toward_capacity(state: JobState, policy: JobPolicy) -> bool:
    """Check whether a state contributes toward capacity limits."""
    if state == JOB_STATE_RUNNING:
        return True
    if state == JOB_STATE_PENDING:
        return policy.count_pending_toward_capacity
    return False


def transition_record(
    records: dict[str, JobRecord],
    job_id: JobId,
    target: JobState,
    policy: JobPolicy,
    clock: Callable[[], Timestamp],
    *,
    result_url: ResultUrl | None = None,
    error: ErrorString | None = None,
    error_category: ErrorCategory | None = None,
    cancellation_reason: CancellationReason | None = None,
    progress_message: ProgressMessage | None = None,
) -> JobStatusSnapshot:
    """Perform an atomic state transition and return the snapshot.

    Mutates the record in-place. Returns the snapshot after transition.
    Raises TaskNotFoundError if job_id not found; InvalidStateTransitionError if transition invalid.
    """
    now = Timestamp(float(clock()))
    record = _get_or_raise(records, job_id)
    validate_transition(record.state, target)

    was_active = _counts_toward_capacity(record.state, policy)
    record.state = target
    record.updated_at = now

    if target == JOB_STATE_RUNNING:
        record.started_at = now
        record.progress = Progress(0.0)
        record.progress_message = None
        record.last_progress_at = None

    if target in TERMINAL_JOB_STATES:
        record.finished_at = now

    if target == JOB_STATE_COMPLETED:
        record.progress = Progress(100.0)
        record.result_url = str(result_url) if result_url is not None else None
        record.progress_message = str(progress_message) if progress_message is not None else None

    if target == JOB_STATE_FAILED:
        record.error = error or ErrorString("Unknown error")
        record.error_category = error_category

    if target == JOB_STATE_CANCELLED:
        record.cancellation_reason = cancellation_reason

    return record.to_snapshot()


def create_record(
    records: dict[str, JobRecord],
    operation_type: str,
    correlation_id: str | None,
    metadata: dict[str, str],
    clock: Callable[[], Timestamp],
) -> tuple[JobId, JobStatusSnapshot]:
    """Create a new job record and return its ID and snapshot.

    Generates a UUID-based job_id. Mutates records dict in-place.
    """
    now = Timestamp(float(clock()))
    job_id = JobId(str(uuid.uuid4()))
    record = JobRecord(
        job_id=job_id,
        operation_type=operation_type,
        correlation_id=correlation_id,
        metadata=metadata,
        created_at=now,
        updated_at=now,
    )
    records[str(job_id)] = record
    return job_id, record.to_snapshot()


def _get_or_raise(records: dict[str, JobRecord], job_id: JobId) -> JobRecord:
    """Get a record or raise if not found."""
    record = records.get(str(job_id))
    if record is None:
        raise TaskNotFoundError(str(job_id))
    return record


def count_active(records: dict[str, JobRecord], policy: JobPolicy) -> int:
    """Count records that contribute toward capacity limits."""
    count = 0
    for record in records.values():
        if record.state == JOB_STATE_RUNNING:
            count += 1
        elif record.state == JOB_STATE_PENDING and policy.count_pending_toward_capacity:
            count += 1
    return count
