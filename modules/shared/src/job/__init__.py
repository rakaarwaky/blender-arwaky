"""Job domain — contracts, taxonomy, and shared types."""

from .contract_job_aggregate import IJobAggregate
from .contract_job_cancel_protocol import JobCancelProtocol
from .contract_job_capacity_protocol import JobCapacityProtocol
from .contract_job_cleanup_protocol import JobCleanupProtocol
from .contract_job_monitor_protocol import JobMonitorProtocol
from .contract_job_tracker_protocol import JobTrackerProtocol
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
    "JobCapacityProtocol",
    "IJobAggregate",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_TIMED_OUT",
    "JobStatus",
]
