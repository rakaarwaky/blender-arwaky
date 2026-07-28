# modules/shared/src/job/taxonomy_job_state_constant.py
from __future__ import annotations

from collections.abc import Mapping
from typing import Final

from ..common.taxonomy_core_vo import JobState

# ============================================================
# JOB STATE CONSTANTS
# ============================================================
JOB_STATE_PENDING: Final[JobState] = JobState("PENDING")
JOB_STATE_RUNNING: Final[JobState] = JobState("RUNNING")
JOB_STATE_COMPLETED: Final[JobState] = JobState("COMPLETED")
JOB_STATE_FAILED: Final[JobState] = JobState("FAILED")
JOB_STATE_CANCELLED: Final[JobState] = JobState("CANCELLED")
JOB_STATE_TIMED_OUT: Final[JobState] = JobState("TIMED_OUT")

# ============================================================
# STATE SETS
# ============================================================
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

# ============================================================
# VALID TRANSITIONS
# ============================================================
VALID_JOB_TRANSITIONS: Final[Mapping[JobState, frozenset[JobState]]] = {
    JOB_STATE_PENDING: frozenset(
        {
            JOB_STATE_RUNNING,
            JOB_STATE_CANCELLED,
        }
    ),
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

# ============================================================
# CANCELLATION OUTCOMES
# ============================================================
CANCELLATION_OUTCOME_ACCEPTED: Final[str] = "ACCEPTED"
CANCELLATION_OUTCOME_ALREADY_TERMINAL: Final[str] = "ALREADY_TERMINAL"
CANCELLATION_OUTCOME_NOT_FOUND: Final[str] = "NOT_FOUND"
CANCELLATION_OUTCOME_UNSUPPORTED: Final[str] = "UNSUPPORTED"
