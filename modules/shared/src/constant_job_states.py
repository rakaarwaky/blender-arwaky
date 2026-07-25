"""Job state constants and factory helpers."""

from __future__ import annotations

from typing import Final

from .constant_core_types import ErrorString, JobId, JobState, Progress, ResultUrl


# ============================================================
# JOB STATE CONSTANTS
# ============================================================

JOB_STATE_PENDING: Final[JobState] = JobState("PENDING")
JOB_STATE_RUNNING: Final[JobState] = JobState("RUNNING")
JOB_STATE_COMPLETED: Final[JobState] = JobState("COMPLETED")
JOB_STATE_FAILED: Final[JobState] = JobState("FAILED")


def create_job_id(raw: str) -> JobId:
    """Factory helper to create a JobId from a raw string."""
    return JobId(raw)


def create_progress(raw: float) -> Progress:
    """Factory helper to create a validated Progress value."""
    if raw < 0.0 or raw > 100.0:
        raise ValueError("progress must be between 0.0 and 100.0")
    return Progress(raw)
