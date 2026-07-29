# modules/shared/src/job/taxonomy_job_entity.py
"""Job domain entity — stateful domain concept with identity."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    Details,
    ErrorString,
    JobId,
    JobState,
    Progress,
    ResultUrl,
    Timestamp,
)
from .taxonomy_job_constant import (
    ACTIVE_JOB_STATES,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    TERMINAL_JOB_STATES,
)
from .taxonomy_job_vo import (
    CancellationReason,
    CorrelationId,
    ErrorCategory,
    JobStatusSnapshot,
    OperationType,
    ProgressMessage,
)


@dataclass
class JobRecord:
    """Mutable internal job record. State holder, not a public read model."""

    job_id: JobId
    operation_type: OperationType
    created_at: Timestamp
    updated_at: Timestamp
    correlation_id: CorrelationId | None = None
    metadata: Details = field(default_factory=dict)
    state: JobState = JOB_STATE_PENDING
    progress: Progress = Progress(0.0)
    progress_message: ProgressMessage | None = None
    result_url: ResultUrl | None = None
    error: ErrorString | None = None
    error_category: ErrorCategory | None = None
    cancellation_reason: CancellationReason | None = None
    started_at: Timestamp | None = None
    finished_at: Timestamp | None = None
    last_progress_at: Timestamp | None = None

    def to_snapshot(self) -> JobStatusSnapshot:
        return JobStatusSnapshot(
            job_id=self.job_id,
            state=self.state,
            operation_type=self.operation_type,
            created_at=self.created_at,
            updated_at=self.updated_at,
            progress=self.progress,
            progress_message=self.progress_message,
            result_url=self.result_url,
            error=self.error,
            error_category=self.error_category,
            correlation_id=self.correlation_id,
            started_at=self.started_at,
            finished_at=self.finished_at,
            metadata=tuple(sorted(self.metadata.items())),
            is_terminal=self.state in TERMINAL_JOB_STATES,
            is_cancellable=self.state in ACTIVE_JOB_STATES,
            progress_applicable=self.state == JOB_STATE_RUNNING,
        )
