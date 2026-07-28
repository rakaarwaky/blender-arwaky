# modules/job/src/capabilities_job_registry.py
from __future__ import annotations

import logging
import threading
import uuid
from collections.abc import Callable
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    Timestamp,
)
from modules.shared.src.job.contract_job_protocol import (
    ICancellationSignaler,
    IJobEventPublisher,
    IJobRegistry,
)
from modules.shared.src.job.taxonomy_job_error import (
    CapacityError,
    InvalidStateTransitionError,
    JobError,
    TaskNotFoundError,
    ValidationError,
)
from modules.shared.src.job.taxonomy_job_state_constant import (
    CANCELLATION_OUTCOME_ACCEPTED,
    CANCELLATION_OUTCOME_ALREADY_TERMINAL,
    CANCELLATION_OUTCOME_NOT_FOUND,
    CANCELLATION_OUTCOME_UNSUPPORTED,
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
    TERMINAL_JOB_STATES,
    VALID_JOB_TRANSITIONS,
)
from modules.shared.src.job.taxonomy_job_status_entity import JobRecord
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    CancellationResult,
    CancelTaskCommand,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    ErrorCategory,
    FailTaskCommand,
    JobPolicy,
    JobStatusSnapshot,
    OperationType,
    ProgressUpdateCommand,
)
from modules.shared.src.job.utility_job_sanitizer import (
    redact_metadata,
    sanitize_cancellation_reason,
    sanitize_error,
    sanitize_progress_message,
    sanitize_text,
)

logger = logging.getLogger("BlenderMCPServer")


class InMemoryJobRegistry(IJobRegistry):
    """
    Thread-safe in-memory job registry capability.

    This capability owns job state and enforces:
    - state machine transitions
    - capacity limits
    - progress rules
    - cancellation outcomes
    - retention cleanup
    - stale running recovery
    """

    def __init__(
        self,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
        cancellation_signaler: ICancellationSignaler | None = None,
        event_publisher: IJobEventPublisher | None = None,
        id_generator: Callable[[], JobId] | None = None,
    ) -> None:
        if policy.max_active < 0:
            raise ValueError("policy.max_active must be >= 0")
        if policy.retention_seconds < 0:
            raise ValueError("policy.retention_seconds must be >= 0")
        if policy.max_records < 0:
            raise ValueError("policy.max_records must be >= 0")
        if policy.stale_running_lifetime_seconds < 0:
            raise ValueError("policy.stale_running_lifetime_seconds must be >= 0")
        if policy.progress_throttle_seconds < 0:
            raise ValueError("policy.progress_throttle_seconds must be >= 0")

        self._policy = policy
        self._clock = clock
        self._cancellation_signaler = cancellation_signaler
        self._event_publisher = event_publisher
        self._new_id = id_generator or (lambda: JobId(str(uuid.uuid4())))

        self._lock = threading.RLock()
        self._records: dict[str, JobRecord] = {}
        self._active_count = 0

    # ============================================================
    # PUBLIC API
    # ============================================================

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        now = self._now()

        operation = sanitize_text(str(command.operation_type), 100)
        if not operation:
            raise ValidationError(ErrorString("operation_type is required"))

        metadata = redact_metadata(command.metadata)

        with self._lock:
            if self._active_count >= self._policy.max_active:
                raise CapacityError(
                    max_active=self._policy.max_active,
                    current_active=self._active_count,
                )

            job_id = self._new_id()
            record = JobRecord(
                job_id=job_id,
                operation_type=OperationType(operation),
                correlation_id=command.correlation_id,
                metadata=metadata,
                created_at=now,
                updated_at=now,
            )

            self._records[str(job_id)] = record

            if self._counts_toward_capacity(record.state):
                self._active_count += 1

            snapshot = record.to_snapshot()

        self._publish_snapshot("job.task.created", snapshot)
        return snapshot

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        snapshot = self._transition(job_id, JOB_STATE_RUNNING, event="job.task.started")
        return snapshot

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        now = self._now()
        progress_value = float(command.progress)

        if progress_value < 0.0 or progress_value > 100.0:
            raise ValidationError(ErrorString("progress must be between 0 and 100"))

        message = sanitize_progress_message(command.message)

        with self._lock:
            record = self._records.get(str(command.job_id))
            if record is None:
                raise TaskNotFoundError(str(command.job_id))

            if record.state != JOB_STATE_RUNNING:
                raise InvalidStateTransitionError(str(record.state), "PROGRESS")

            if progress_value < float(record.progress):
                raise ValidationError(ErrorString("progress must be monotonic"))

            # Throttle non-final progress updates.
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

        self._publish_snapshot("job.task.progress_updated", snapshot)
        return snapshot

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        summary = sanitize_progress_message(command.summary)
        snapshot = self._transition(
            command.job_id,
            JOB_STATE_COMPLETED,
            result_url=command.result_url,
            progress_message=summary,
            event="job.task.completed",
        )
        return snapshot

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        error = sanitize_error(command.error_message)
        if not str(error).strip():
            raise ValidationError(ErrorString("error_message is required"))

        category: ErrorCategory | None = None
        if command.error_category:
            raw_category = sanitize_text(str(command.error_category), 100)
            category = ErrorCategory(raw_category) if raw_category else None

        snapshot = self._transition(
            command.job_id,
            JOB_STATE_FAILED,
            error=error,
            error_category=category,
            event="job.task.failed",
        )
        return snapshot

    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult:
        reason = sanitize_cancellation_reason(command.reason)

        with self._lock:
            record = self._records.get(str(command.job_id))
            if record is None:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_NOT_FOUND,
                    message="Task not found",
                )

            if record.state in TERMINAL_JOB_STATES:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_ALREADY_TERMINAL,
                    message=f"Task already in terminal state {record.state}",
                )

            current_state = record.state

        # Pending tasks cancel immediately.
        if current_state == JOB_STATE_RUNNING:
            if self._cancellation_signaler is None:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_UNSUPPORTED,
                    message="Executor does not support cancellation",
                )

            try:
                signaled = self._cancellation_signaler.signal(command.job_id, reason)
            except Exception:
                logger.exception("Cancellation signaler failed for job %s", command.job_id)
                signaled = False

            if not signaled:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_UNSUPPORTED,
                    message="Executor could not be signaled",
                )

        try:
            self._transition(
                command.job_id,
                JOB_STATE_CANCELLED,
                cancellation_reason=reason,
                event="job.task.cancelled",
            )
        except TaskNotFoundError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_OUTCOME_NOT_FOUND,
                message="Task not found",
            )
        except InvalidStateTransitionError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_OUTCOME_ALREADY_TERMINAL,
                message="Task reached terminal state before cancellation applied",
            )

        return CancellationResult(
            job_id=command.job_id,
            accepted=True,
            outcome=CANCELLATION_OUTCOME_ACCEPTED,
            message="Cancellation accepted",
        )

    def get_snapshot(self, job_id: JobId) -> JobStatusSnapshot:
        with self._lock:
            record = self._records.get(str(job_id))
            if record is None:
                raise TaskNotFoundError(str(job_id))
            return record.to_snapshot()

    def cleanup_expired(self) -> CleanupSummary:
        now = self._now()
        warnings: list[str] = []
        events: list[tuple[str, JobStatusSnapshot]] = []

        with self._lock:
            reclaimed_capacity = 0

            # 1) Stale running recovery.
            if self._policy.stale_recovery_enabled:
                for record in list(self._records.values()):
                    if record.state != JOB_STATE_RUNNING:
                        continue
                    if record.started_at is None:
                        continue

                    age = float(now) - float(record.started_at)
                    if age <= self._policy.stale_running_lifetime_seconds:
                        continue

                    try:
                        snapshot = self._apply_transition_locked(
                            record,
                            JOB_STATE_TIMED_OUT,
                            now,
                            error=ErrorString("Task exceeded maximum running lifetime"),
                            error_category=ErrorCategory("TIMEOUT"),
                        )
                        reclaimed_capacity += 1
                        events.append(("job.task.timed_out", snapshot))
                    except JobError as exc:
                        warnings.append(f"stale_transition_failed: {exc}")

            # 2) Retention purge, oldest terminal first.
            terminal = [r for r in self._records.values() if r.state in TERMINAL_JOB_STATES]
            terminal.sort(key=lambda r: float(r.finished_at if r.finished_at is not None else r.updated_at))

            purge_ids: set[str] = set()

            for record in terminal:
                finished = float(record.finished_at if record.finished_at is not None else record.updated_at)
                if float(now) - finished >= self._policy.retention_seconds:
                    purge_ids.add(str(record.job_id))

            remaining_terminal = [r for r in terminal if str(r.job_id) not in purge_ids]

            # 3) Max retained terminal records.
            if len(remaining_terminal) > self._policy.max_records:
                excess = len(remaining_terminal) - self._policy.max_records
                for record in remaining_terminal[:excess]:
                    purge_ids.add(str(record.job_id))

            for job_id in purge_ids:
                self._records.pop(job_id, None)

            retained = len(self._records)

            summary = CleanupSummary(
                purged=len(purge_ids),
                retained=retained,
                reclaimed_capacity=reclaimed_capacity,
                warnings=tuple(warnings),
            )

        for event_name, snapshot in events:
            self._publish_snapshot(event_name, snapshot)

        self._publish_raw(
            "job.task.cleanup_sweep",
            {
                "purged": summary.purged,
                "retained": summary.retained,
                "reclaimed_capacity": summary.reclaimed_capacity,
                "warnings": list(summary.warnings),
            },
        )

        return summary

    def capacity_status(self) -> CapacityStatus:
        with self._lock:
            active = self._active_count
            limit = self._policy.max_active
            available = max(0, limit - active)
            return CapacityStatus(active=active, limit=limit, available=available)

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _now(self) -> Timestamp:
        return Timestamp(float(self._clock()))

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
        result_url: Any | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: Any | None = None,
        event: str | None = None,
    ) -> JobStatusSnapshot:
        now = self._now()

        with self._lock:
            record = self._records.get(str(job_id))
            if record is None:
                raise TaskNotFoundError(str(job_id))

            snapshot = self._apply_transition_locked(
                record,
                target,
                now,
                result_url=result_url,
                error=error,
                error_category=error_category,
                cancellation_reason=cancellation_reason,
                progress_message=progress_message,
            )

        event_name = event or f"job.task.{str(target).lower()}"
        self._publish_snapshot(event_name, snapshot)
        return snapshot

    def _apply_transition_locked(
        self,
        record: JobRecord,
        target: JobState,
        now: Timestamp,
        *,
        result_url: Any | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: Any | None = None,
    ) -> JobStatusSnapshot:
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
            record.result_url = result_url
            if progress_message is not None:
                record.progress_message = progress_message

        if target == JOB_STATE_FAILED:
            record.error = error or ErrorString("Unknown error")
            record.error_category = error_category

        if target == JOB_STATE_CANCELLED:
            record.cancellation_reason = cancellation_reason

        now_active = self._counts_toward_capacity(target)
        delta = (1 if now_active else 0) - (1 if was_active else 0)
        self._active_count += delta

        if self._active_count < 0:
            logger.warning("Active job count became negative; resetting to zero")
            self._active_count = 0

        return record.to_snapshot()

    def _publish_snapshot(self, event: str, snapshot: JobStatusSnapshot) -> None:
        if self._event_publisher is None:
            return

        payload = {
            "job_id": str(snapshot.job_id),
            "state": str(snapshot.state),
            "operation_type": str(snapshot.operation_type),
            "progress": float(snapshot.progress),
            "correlation_id": str(snapshot.correlation_id) if snapshot.correlation_id else None,
            "is_terminal": snapshot.is_terminal,
            "created_at": float(snapshot.created_at),
            "updated_at": float(snapshot.updated_at),
            "started_at": float(snapshot.started_at) if snapshot.started_at is not None else None,
            "finished_at": float(snapshot.finished_at) if snapshot.finished_at is not None else None,
        }

        self._publish_raw(event, payload)

    def _publish_raw(self, event: str, payload: dict[str, Any]) -> None:
        if self._event_publisher is None:
            return

        try:
            self._event_publisher.publish(event, payload)
        except Exception:
            logger.exception("Failed publishing job event: %s", event)
