"""Job domain — contracts, taxonomy, and shared types."""

from .contract_job_aggregate import (
    JobCancelProtocol,
    JobCleanupProtocol,
    JobMonitorProtocol,
    JobTrackerProtocol,
)
from .taxonomy_job_state_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
)
from .taxonomy_job_status_entity import JobStatus

__all__ = [
    "JobTrackerProtocol",
    "JobMonitorProtocol",
    "JobCancelProtocol",
    "JobCleanupProtocol",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_TIMED_OUT",
    "JobStatus",
]