"""Job state constants."""

from __future__ import annotations

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
