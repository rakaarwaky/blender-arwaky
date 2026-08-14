# modules/shared/src/job/taxonomy_job_constant.py
"""Job domain constants — compile-time literal values."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final

from ..common.taxonomy_core_vo import JobState

# ─── Job States ──────────────────────────────────────────────────────────────
JOB_STATE_PENDING: Final[JobState] = JobState("PENDING")
JOB_STATE_RUNNING: Final[JobState] = JobState("RUNNING")
JOB_STATE_COMPLETED: Final[JobState] = JobState("COMPLETED")
JOB_STATE_FAILED: Final[JobState] = JobState("FAILED")
JOB_STATE_CANCELLED: Final[JobState] = JobState("CANCELLED")
JOB_STATE_TIMED_OUT: Final[JobState] = JobState("TIMED_OUT")

# ─── State Sets ──────────────────────────────────────────────────────────────
ACTIVE_JOB_STATES: Final[frozenset[JobState]] = frozenset(
    {
        JOB_STATE_PENDING,
        JOB_STATE_RUNNING,
    }
)

TERMINAL_JOB_STATES: Final[frozenset[JobState]] = frozenset(
    {
        JOB_STATE_COMPLETED,
        JOB_STATE_FAILED,
        JOB_STATE_CANCELLED,
        JOB_STATE_TIMED_OUT,
    }
)

# ─── Valid Transitions ───────────────────────────────────────────────────────
VALID_JOB_TRANSITIONS: Final[Mapping[JobState, frozenset[JobState]]] = {
    JOB_STATE_PENDING: frozenset({JOB_STATE_RUNNING, JOB_STATE_CANCELLED}),
    JOB_STATE_RUNNING: frozenset(
        {
            JOB_STATE_COMPLETED,
            JOB_STATE_FAILED,
            JOB_STATE_CANCELLED,
            JOB_STATE_TIMED_OUT,
        }
    ),
    JOB_STATE_COMPLETED: frozenset(),
    JOB_STATE_FAILED: frozenset(),
    JOB_STATE_CANCELLED: frozenset(),
    JOB_STATE_TIMED_OUT: frozenset(),
}

# ─── Cancellation Outcomes ───────────────────────────────────────────────────
CANCELLATION_ACCEPTED: Final[str] = "ACCEPTED"
CANCELLATION_ALREADY_TERMINAL: Final[str] = "ALREADY_TERMINAL"
CANCELLATION_NOT_FOUND: Final[str] = "NOT_FOUND"
CANCELLATION_UNSUPPORTED: Final[str] = "UNSUPPORTED"

# ─── Event Types ─────────────────────────────────────────────────────────────
EVENT_TASK_CREATED: Final[str] = "job.task.created"
EVENT_TASK_STARTED: Final[str] = "job.task.started"
EVENT_TASK_PROGRESS: Final[str] = "job.task.progress_updated"
EVENT_TASK_COMPLETED: Final[str] = "job.task.completed"
EVENT_TASK_FAILED: Final[str] = "job.task.failed"
EVENT_TASK_CANCELLED: Final[str] = "job.task.cancelled"
EVENT_TASK_TIMED_OUT: Final[str] = "job.task.timed_out"
EVENT_CLEANUP_SWEEP: Final[str] = "job.task.cleanup_sweep"
EVENT_CAPACITY_REJECTED: Final[str] = "job.task.capacity_rejected"

# ─── Sanitization Limits ─────────────────────────────────────────────────────
MAX_OPERATION_TYPE_LENGTH: Final[int] = 100
MAX_PROGRESS_MESSAGE_LENGTH: Final[int] = 500
MAX_ERROR_LENGTH: Final[int] = 1000
MAX_CANCELLATION_REASON_LENGTH: Final[int] = 500
MAX_METADATA_KEYS: Final[int] = 50
MAX_METADATA_KEY_LENGTH: Final[int] = 100
MAX_METADATA_VALUE_LENGTH: Final[int] = 200
MAX_ERROR_CATEGORY_LENGTH: Final[int] = 100
