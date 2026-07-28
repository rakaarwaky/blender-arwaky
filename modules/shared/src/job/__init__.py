"""Job domain — contracts, taxonomy, and shared types."""
from .contract_job_aggregate import IJobAggregate
from .contract_job_protocol import (
    IJobCancellation,
    IJobCapacity,
    IJobCleanup,
    IJobLifecycle,
    IJobMonitor,
)
from .taxonomy_job_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
)

__all__ = [
    "IJobAggregate",
    "IJobCancellation",
    "IJobCapacity",
    "IJobCleanup",
    "IJobLifecycle",
    "IJobMonitor",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_TIMED_OUT",
]
