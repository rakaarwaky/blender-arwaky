# modules/shared/src/job/taxonomy_job_vo.py
"""Job domain value objects — immutable data concepts."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import NewType

from ..common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    ResultUrl,
    Timestamp,
)

# ─── Branded Types ───────────────────────────────────────────────────────────
OperationType = NewType("OperationType", str)
CorrelationId = NewType("CorrelationId", str)
ProgressMessage = NewType("ProgressMessage", str)
CancellationReason = NewType("CancellationReason", str)
ErrorCategory = NewType("ErrorCategory", str)
TaskMetadata = NewType("TaskMetadata", Mapping[str, str])

# ─── Policy ──────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class JobPolicy:
    max_active: int = 100
    retention_seconds: float = 3600.0
    max_records: int = 1000
    stale_recovery_enabled: bool = True
    stale_running_lifetime_seconds: float = 1800.0
    progress_throttle_seconds: float = 0.5
    count_pending_toward_capacity: bool = True

# ─── Commands ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CreateTaskCommand:
    operation_type: OperationType
    correlation_id: CorrelationId | None = None
    metadata: TaskMetadata | None = None

@dataclass(frozen=True)
class ProgressUpdateCommand:
    job_id: JobId
    progress: Progress
    message: ProgressMessage | None = None

@dataclass(frozen=True)
class CompleteTaskCommand:
    job_id: JobId
    result_url: ResultUrl | None = None
    summary: ProgressMessage | None = None

@dataclass(frozen=True)
class FailTaskCommand:
    job_id: JobId
    error_message: ErrorString
    error_category: ErrorCategory | None = None

@dataclass(frozen=True)
class CancelTaskCommand:
    job_id: JobId
    reason: CancellationReason | None = None

# ─── Read Models / Results ───────────────────────────────────────────────────

@dataclass(frozen=True)
class JobStatusSnapshot:
    job_id: JobId
    state: JobState
    operation_type: OperationType
    created_at: Timestamp
    updated_at: Timestamp
    progress: Progress = Progress(0.0)
    progress_message: ProgressMessage | None = None
    result_url: ResultUrl | None = None
    error: ErrorString | None = None
    error_category: ErrorCategory | None = None
    correlation_id: CorrelationId | None = None
    started_at: Timestamp | None = None
    finished_at: Timestamp | None = None
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    is_terminal: bool = False
    is_cancellable: bool = False
    progress_applicable: bool = False

@dataclass(frozen=True)
class CancellationResult:
    job_id: JobId
    accepted: bool
    outcome: str
    message: str

@dataclass(frozen=True)
class CleanupDecision:
    purge_ids: tuple[JobId, ...] = field(default_factory=tuple)
    stale_timeout_ids: tuple[JobId, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class CleanupSummary:
    purged: int
    retained: int
    reclaimed_capacity: int
    warnings: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class CapacityDecision:
    accepted: bool
    active: int
    limit: int
    available: int
    reason: str = ""

@dataclass(frozen=True)
class CapacityStatus:
    active: int
    limit: int
    available: int
