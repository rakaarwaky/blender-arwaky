# modules/shared/src/job/taxonomy_job_event.py
"""Job domain events — immutable domain facts."""
from __future__ import annotations

from dataclasses import dataclass

from ..common.taxonomy_core_vo import JobId, JobState, Progress, Timestamp
from .taxonomy_job_vo import CorrelationId, OperationType


@dataclass(frozen=True)
class JobEvent:
    """Immutable record of a job lifecycle occurrence."""

    event_type: str
    job_id: JobId
    operation_type: OperationType
    state_after: JobState
    timestamp: Timestamp
    state_before: JobState | None = None
    progress: Progress | None = None
    correlation_id: CorrelationId | None = None
    reason: str | None = None