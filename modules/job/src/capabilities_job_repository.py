# modules/job/src/capabilities_job_repository.py
"""Capability: Job lifecycle repository (FR-JOB-001).

Owns in-memory task records. Enforces state machine.
All transitions atomic and thread-safe.
"""
from __future__ import annotations

import logging
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
from modules.shared.src.job.contract_job_lifecycle_protocol import IJobLifecycle
from modules.shared.src.job.taxonomy_job_constant import (
    EVENT_TASK_CANCELLED,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_CREATED,
    EVENT_TASK_FAILED,
    EVENT_TASK_PROGRESS,
    EVENT_TASK_STARTED,
    EVENT_TASK_TIMED_OUT,
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
    ValidationError,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    CompleteTaskCommand,
    CreateTaskCommand,
    ErrorCategory,
    FailTaskCommand,
    JobPolicy,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)
from modules.shared.src.job.utility_job_sanitizer import (
    redact_metadata,
    sanitize_error,
    sanitize_error_category,
    sanitize_operation_type,
    sanitize_progress_message,
)

logger = logging.getLogger("BlenderMCPServer")


# ─── Block 1: Class Definition & Constructor ─────────────────────────────────


class InMemoryJobLifecycleRepository(IJobLifecycle):
    """Thread-safe in-memory repository owning all job records."""

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
        self._records: dict[str, JobRecord] = {}
        self._active_count: int = 0

    # ─── Block 2: Domain Protocol Method Implementation ──────────────────────

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        now = self._now()
        operation = sanitize_operation_type(str(command.operation_type))
        if not str(operation).strip():
            raise ValidationError(ErrorString("operation_type is required"))

        metadata = redact_metadata(command.metadata)

        with self._lock:
            job_id = self._new_id()
            record = JobRecord(
                job_id=job_id,
                operation_type=operation,
                correlation_id=command.correlation_id,
                metadata=metadata,
                created_at=now,
                updated_at=now,
            )
            self._records[str(job_id)] = record
            if self._counts_toward_capacity(record.state):
                self._active_count += 1
            snapshot = record.to_snapshot()

        self._emit(EVENT_TASK_CREATED, snapshot)
        return snapshot

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        snapshot = self._transition(job_id, JOB_STATE_RUNNING)
        self._emit(EVENT_TASK_STARTED, snapshot)
        return snapshot

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        now = self._now()
        progress_value = float(command.progress)

        if progress_value < 0.0 or progress_value > 100.0:
            raise ValidationError(ErrorString("progress must be between 0 and 100"))

        message = sanitize_progress_message(
            str(command.message) if command.message else None
        )

        with self._lock:
            record = self._get_or_raise(command.job_id)

            if record.state != JOB_STATE_RUNNING:
                raise InvalidStateTransitionError(str(record.state), "PROGRESS")

            if progress_value < float(record.progress):
                raise ValidationError(ErrorString("progress must be monotonic"))

            if (
                record.last_progress_at is not None
                and (float(now) - float(record.last_progress_at))
                < self._policy.progress_throttle_seconds
                and progress_value < 100.0
            ):
                return record.to_snapshot()

            record.progress = Progress(progress_value)
            record.progress_message = message
            record.updated_at = now
            record.last_progress_at = now
            snapshot = record.to_snapshot()

        self._emit(EVENT_TASK_PROGRESS, snapshot)
        return snapshot

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        summary = sanitize_progress_message(
            str(command.summary) if command.summary else None
        )
        snapshot = self._transition(
            command.job_id,
            JOB_STATE_COMPLETED,
            result_url=command.result_url,
            progress_message=summary,
        )
        self._emit(EVENT_TASK_COMPLETED, snapshot)
        return snapshot

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        error = sanitize_error(command.error_message)
        if not str(error).strip():
            raise ValidationError(ErrorString("error_message is required"))

        category: ErrorCategory | None = None
        if command.error_category:
            category = sanitize_error_category(str(command.error_category))

        snapshot = self._transition(
            command.job_id,
            JOB_STATE_FAILED,
            error=error,
            error_category=category,
        )
        self._emit(EVENT_TASK_FAILED, snapshot)
        return snapshot

    def apply_cancel(self, job_id: JobId, reason: CancellationReason | None) -> JobStatusSnapshot:
        snapshot = self._transition(job_id, JOB_STATE_CANCELLED, cancellation_reason=reason)
        self._emit(EVENT_TASK_CANCELLED, snapshot)
        return snapshot

    def apply_timeout(self, job_id: JobId) -> JobStatusSnapshot:
        snapshot = self._transition(
            job_id,
            JOB_STATE_TIMED_OUT,
            error=ErrorString("Task exceeded maximum running lifetime"),
            error_category=ErrorCategory("TIMEOUT"),
        )
        self._emit(EVENT_TASK_TIMED_OUT, snapshot)
        return snapshot

    def get_record(self, job_id: JobId) -> JobStatusSnapshot:
        with self._lock:
            return self._get_or_raise(job_id).to_snapshot()

    def list_terminal(self) -> tuple[JobStatusSnapshot, ...]:
        with self._lock:
            return tuple(
                r.to_snapshot()
                for r in self._records.values()
                if r.state in TERMINAL_JOB_STATES
            )

    def list_running(self) -> tuple[JobStatusSnapshot, ...]:
        with self._lock:
            return tuple(
                r.to_snapshot()
                for r in self._records.values()
                if r.state == JOB_STATE_RUNNING
            )

    def delete_records(self, job_ids: tuple[JobId, ...]) -> int:
        with self._lock:
            deleted = 0
            for jid in job_ids:
                if str(jid) in self._records:
                    del self._records[str(jid)]
                    deleted += 1
            return deleted

    def active_count(self) -> int:
        with self._lock:
            return self._active_count

    # ─── Block 3: Dunder Methods, Factories, and Private Helpers ─────────────

    def __repr__(self) -> str:
        return (
            f"<InMemoryJobLifecycleRepository "
            f"records={len(self._records)} active={self._active_count}>"
        )

    def _now(self) -> Timestamp:
        return Timestamp(float(self._clock()))

    def _get_or_raise(self, job_id: JobId) -> JobRecord:
        record = self._records.get(str(job_id))
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

    def _transition(
        self,
        job_id: JobId,
        target: JobState,
        *,
        result_url: object | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: object | None = None,
    ) -> JobStatusSnapshot:
        now = self._now()
        with self._lock:
            record = self._get_or_raise(job_id)
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
            self._active_count = max(0, self._active_count + delta)

            return record.to_snapshot()

    def _emit(self, event_type: str, snapshot: JobStatusSnapshot) -> None:
        logger.info(
            "Job event: %s job=%s state=%s op=%s",
            event_type,
            snapshot.job_id,
            snapshot.state,
            snapshot.operation_type,
        )
