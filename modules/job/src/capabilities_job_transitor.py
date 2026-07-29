"""Capability: Job state transitor (FR-JOB-001).

Handles atomic state transitions for job lifecycle operations.
Encapsulates transition validation, state mutation, and capacity tracking.
Separated from repository to follow single-responsibility principle.
"""
from __future__ import annotations

import threading
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
    JOB_STATE_TIMED_OUT,
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


class JobStateTransitor:
    """Encapsulates job state transition logic and capacity tracking.

    Separated from InMemoryJobLifecycleRepository to follow single-responsibility:
    this class owns transition validation and state mutation, while the
    repository owns persistence concerns (storage, retrieval, listing).
    """

    def __init__(
        self,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
        id_generator: Callable[[], JobId] | None = None,
    ) -> None:
        self._policy = policy
        self._clock = clock
        self._new_id = id_generator or (lambda: JobId(str(uuid.uuid4())))
        self._lock = threading.RLock()

    def transition(
        self,
        records: dict[str, JobRecord],
        job_id: JobId,
        target: JobState,
        *,
        result_url: ResultUrl | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: ProgressMessage | None = None,
    ) -> JobStatusSnapshot:
        """Perform an atomic state transition with capacity tracking.

        Returns the snapshot after transition. Raises on validation failure.
        """
        now = Timestamp(float(self._clock()))
        with self._lock:
            record = self._get_or_raise(records, job_id)
            self._assert_transition(record.state, target)

            was_active = self._counts_toward_capacity(record.state)
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
                if progress_message is not None:
                    record.progress_message = str(progress_message) if progress_message is not None else None

            if target == JOB_STATE_FAILED:
                record.error = error or ErrorString("Unknown error")
                record.error_category = error_category

            if target == JOB_STATE_CANCELLED:
                record.cancellation_reason = cancellation_reason

            now_active = self._counts_toward_capacity(target)
            delta = (1 if now_active else 0) - (1 if was_active else 0)
            # Capacity delta is tracked by the repository; this class returns the snapshot
            return record.to_snapshot()

    def create_record(
        self,
        records: dict[str, JobRecord],
        operation_type: str,
        correlation_id: str,
        metadata: dict[str, str],
    ) -> tuple[JobId, JobStatusSnapshot]:
        """Create a new job record and return its ID and snapshot.

        Returns the generated job_id and the initial snapshot.
        """
        now = Timestamp(float(self._clock()))
        with self._lock:
            job_id = JobId(str(self._new_id()))
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

    def active_count(self, records: dict[str, JobRecord], policy: JobPolicy) -> int:
        """Count records that contribute toward capacity limits."""
        count = 0
        for record in records.values():
            if record.state == JOB_STATE_RUNNING:
                count += 1
            elif record.state == JOB_STATE_PENDING and policy.count_pending_toward_capacity:
                count += 1
        return count

    def get_or_raise(self, records: dict[str, JobRecord], job_id: JobId) -> JobRecord:
        """Get a record or raise if not found."""
        record = records.get(str(job_id))
        if record is None:
            raise TaskNotFoundError(str(job_id))
        return record

    # ─── Private Helpers ─────────────────────────────────────────────────────

    def _get_or_raise(self, records: dict[str, JobRecord], job_id: JobId) -> JobRecord:
        record = records.get(str(job_id))
        if record is None:
            raise TaskNotFoundError(str(job_id))
        return record

    def _counts_toward_capacity(self, state: JobState) -> bool:
        if state == JOB_STATE_RUNNING:
            return True
        if state == JOB_STATE_PENDING:
            return self._policy.count_pending_toward_capacity
        return False

    def _assert_transition(self, current: JobState, target: JobState) -> None:
        allowed = VALID_JOB_TRANSITIONS.get(current, frozenset())
        if target not in allowed:
            raise InvalidStateTransitionError(str(current), str(target))
