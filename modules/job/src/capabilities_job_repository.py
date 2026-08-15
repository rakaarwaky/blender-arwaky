# modules/job/src/capabilities_job_repository.py
"""Capability: Job lifecycle repository (FR-JOB-001).

Owns in-memory task records. Enforces state machine.
All transitions atomic and thread-safe.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    Timestamp,
)
from modules.shared.src.job.contract_job_event_protocol import IJobEventPublisher
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
)
from modules.shared.src.job.taxonomy_job_entity import JobRecord
from modules.shared.src.job.taxonomy_job_error import (
    InvalidStateTransitionError,
    JobValidationError,
    TaskNotFoundError,
)
from modules.shared.src.job.taxonomy_job_event import JobEvent
from modules.shared.src.job.taxonomy_job_vo import (
    ActiveCount,
    CancellationReason,
    CompleteTaskCommand,
    CorrelationId,
    CreateTaskCommand,
    DeletedCount,
    ErrorCategory,
    FailTaskCommand,
    JobPolicy,
    JobStatusSnapshot,
    OperationType,
    ProgressMessage,
    ProgressUpdateCommand,
    ResultUrl,
)
from modules.shared.src.job.utility_job_sanitizer import (
    redact_metadata,
    sanitize_cancellation_reason,
    sanitize_error,
    sanitize_error_category,
    sanitize_operation_type,
    sanitize_progress_message,
)
from modules.shared.src.job.utility_job_transition import (
    count_active,
    create_record,
    transition_record,
)

logger = logging.getLogger("BlenderMCPServer")


# ─── Block 1: Class Definition & Constructor ─────────────────────────────────


class InMemoryJobLifecycleRepository(IJobLifecycle):
    """Thread-safe in-memory repository owning all job records."""

    def __init__(
        self,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
        event_publisher: IJobEventPublisher,
    ) -> None:
        self._policy = policy
        self._clock = clock
        self._lock = threading.RLock()
        self._records: dict[str, JobRecord] = {}
        self._active_count: int = 0
        self._event_publisher = event_publisher

    # ─── Block 2: Domain Protocol Method Implementation ──────────────────────

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        operation = sanitize_operation_type(str(command.operation_type))
        if not str(operation).strip():
            raise JobValidationError(ErrorString("operation_type is required"))

        metadata = redact_metadata(command.metadata)

        with self._lock:
            job_id, snapshot = create_record(
                self._records,
                str(operation),
                str(command.correlation_id) if command.correlation_id else None,
                metadata if metadata else {},
                self._clock,
            )
            # Track capacity for newly created pending task
            if self._counts_toward_capacity(snapshot.state):
                self._active_count += 1

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
            raise JobValidationError(ErrorString("progress must be between 0 and 100"))

        message = sanitize_progress_message(str(command.message) if command.message else None)

        with self._lock:
            record = self._get_or_raise(command.job_id)

            if record.state != JOB_STATE_RUNNING:
                raise InvalidStateTransitionError(str(record.state), "PROGRESS")

            if progress_value < float(record.progress):
                raise JobValidationError(ErrorString("progress must be monotonic"))

            if (
                record.last_progress_at is not None
                and (float(now) - float(record.last_progress_at)) < self._policy.progress_throttle_seconds
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
        summary = sanitize_progress_message(str(command.summary) if command.summary else None)
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
            raise JobValidationError(ErrorString("error_message is required"))

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
        safe_reason = sanitize_cancellation_reason(reason)
        snapshot = self._transition(job_id, JOB_STATE_CANCELLED, cancellation_reason=safe_reason)
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
            return tuple(r.to_snapshot() for r in self._records.values() if r.state in TERMINAL_JOB_STATES)

    def list_running(self) -> tuple[JobStatusSnapshot, ...]:
        with self._lock:
            return tuple(r.to_snapshot() for r in self._records.values() if r.state == JOB_STATE_RUNNING)

    def delete_records(self, job_ids: tuple[JobId, ...]) -> DeletedCount:
        with self._lock:
            deleted = 0
            for jid in job_ids:
                if str(jid) in self._records:
                    del self._records[str(jid)]
                    deleted += 1
            return DeletedCount(deleted)

    def active_count(self) -> ActiveCount:
        with self._lock:
            return ActiveCount(count_active(self._records, self._policy))

    # ─── Block 3: Dunder Methods, Factories, and Private Helpers ─────────────

    def __repr__(self) -> str:
        return f"<InMemoryJobLifecycleRepository records={len(self._records)} active={self._active_count}>"

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

    def _transition(
        self,
        job_id: JobId,
        target: JobState,
        *,
        result_url: ResultUrl | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: ProgressMessage | None = None,
    ) -> JobStatusSnapshot:
        with self._lock:
            record = self._get_or_raise(job_id)
            was_active = self._counts_toward_capacity(record.state)

            snapshot = transition_record(
                self._records,
                job_id,
                target,
                self._policy,
                self._clock,
                result_url=result_url,
                error=error,
                error_category=error_category,
                cancellation_reason=cancellation_reason,
                progress_message=progress_message,
            )

            now_active = self._counts_toward_capacity(target)
            delta = (1 if now_active else 0) - (1 if was_active else 0)
            self._active_count = max(0, self._active_count + delta)

            return snapshot

    def _emit(self, event_type: str, snapshot: JobStatusSnapshot) -> None:
        """Emit a job event through the configured event publisher."""
        event = JobEvent(
            event_type=event_type,
            job_id=snapshot.job_id,
            operation_type=snapshot.operation_type,
            state_after=snapshot.state,
            timestamp=snapshot.updated_at,
            state_before=None,
            progress=snapshot.progress,
            correlation_id=snapshot.correlation_id,
        )
        self._event_publisher.emit(event)


class JsonFileJobLifecycleRepository(InMemoryJobLifecycleRepository):
    """Atomic JSON-backed Job repository for CLI/process boundary access.

    The JSON file stores sanitized public snapshots only. Reads refresh from
    disk before lookup and writes use temp-file plus ``os.replace`` so a second
    CLI process never observes a partial document.
    """

    def __init__(
        self,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
        event_publisher: IJobEventPublisher,
        storage_path: str | os.PathLike[str],
    ) -> None:
        super().__init__(policy=policy, clock=clock, event_publisher=event_publisher)
        self._storage_path = Path(storage_path)
        self._persistence_lock = threading.RLock()
        self._refresh_from_disk()

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().create_task(command)
            self._persist()
            return snapshot

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().start_task(job_id)
            self._persist()
            return snapshot

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().update_progress(command)
            self._persist()
            return snapshot

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().complete_task(command)
            self._persist()
            return snapshot

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().fail_task(command)
            self._persist()
            return snapshot

    def apply_cancel(self, job_id: JobId, reason: CancellationReason | None) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().apply_cancel(job_id, reason)
            self._persist()
            return snapshot

    def apply_timeout(self, job_id: JobId) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            snapshot = super().apply_timeout(job_id)
            self._persist()
            return snapshot

    def get_record(self, job_id: JobId) -> JobStatusSnapshot:
        with self._persistence_lock:
            self._refresh_from_disk()
            return super().get_record(job_id)

    def list_terminal(self) -> tuple[JobStatusSnapshot, ...]:
        with self._persistence_lock:
            self._refresh_from_disk()
            return super().list_terminal()

    def list_running(self) -> tuple[JobStatusSnapshot, ...]:
        with self._persistence_lock:
            self._refresh_from_disk()
            return super().list_running()

    def active_count(self) -> ActiveCount:
        with self._persistence_lock:
            self._refresh_from_disk()
            return super().active_count()

    def delete_records(self, job_ids: tuple[JobId, ...]) -> DeletedCount:
        with self._persistence_lock:
            self._refresh_from_disk()
            deleted = super().delete_records(job_ids)
            self._persist()
            return deleted

    def _refresh_from_disk(self) -> None:
        if not self._storage_path.is_file():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
            records = payload.get("records", []) if isinstance(payload, dict) else []
            if not isinstance(records, list):
                return
            with self._lock:
                self._records = {
                    str(item["job_id"]): self._record_from_dict(item) for item in records if isinstance(item, dict)
                }
                self._active_count = int(count_active(self._records, self._policy))
        except (OSError, ValueError, TypeError, KeyError):
            logger.warning("Ignoring corrupt job store: %s", self._storage_path)

    def _persist(self) -> None:
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            payload = {
                "version": 1,
                "records": [self._snapshot_to_dict(record.to_snapshot()) for record in self._records.values()],
            }
        fd, temporary = tempfile.mkstemp(dir=str(self._storage_path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._storage_path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(temporary)
            raise

    @staticmethod
    def _snapshot_to_dict(snapshot: JobStatusSnapshot) -> dict[str, object]:
        return {
            "job_id": str(snapshot.job_id),
            "state": str(snapshot.state),
            "operation_type": str(snapshot.operation_type),
            "created_at": float(snapshot.created_at),
            "updated_at": float(snapshot.updated_at),
            "progress": float(snapshot.progress),
            "progress_message": str(snapshot.progress_message) if snapshot.progress_message is not None else None,
            "result_url": str(snapshot.result_url) if snapshot.result_url is not None else None,
            "error": str(snapshot.error) if snapshot.error is not None else None,
            "error_category": str(snapshot.error_category) if snapshot.error_category is not None else None,
            "correlation_id": str(snapshot.correlation_id) if snapshot.correlation_id is not None else None,
            "started_at": float(snapshot.started_at) if snapshot.started_at is not None else None,
            "finished_at": float(snapshot.finished_at) if snapshot.finished_at is not None else None,
            "metadata": list(snapshot.metadata),
        }

    @staticmethod
    def _record_from_dict(data: dict[str, object]) -> JobRecord:
        metadata = data.get("metadata", [])
        return JobRecord(
            job_id=JobId(str(data["job_id"])),
            operation_type=OperationType(str(data.get("operation_type", "unknown"))),
            created_at=Timestamp(float(data.get("created_at", 0.0))),
            updated_at=Timestamp(float(data.get("updated_at", 0.0))),
            correlation_id=CorrelationId(str(data["correlation_id"])) if data.get("correlation_id") else None,
            metadata=dict(metadata) if isinstance(metadata, list) else {},
            state=JobState(str(data.get("state", JOB_STATE_PENDING))),
            progress=Progress(float(data.get("progress", 0.0))),
            progress_message=ProgressMessage(str(data["progress_message"])) if data.get("progress_message") else None,
            result_url=ResultUrl(str(data["result_url"])) if data.get("result_url") else None,
            error=ErrorString(str(data["error"])) if data.get("error") else None,
            error_category=ErrorCategory(str(data["error_category"])) if data.get("error_category") else None,
            started_at=Timestamp(float(data["started_at"])) if data.get("started_at") is not None else None,
            finished_at=Timestamp(float(data["finished_at"])) if data.get("finished_at") is not None else None,
        )
