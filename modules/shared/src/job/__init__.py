"""Job domain — contracts, taxonomy, and shared types."""

from .contract_job_aggregate import IJobAggregate
from .contract_job_cancellation_protocol import IJobCancellation
from .contract_job_capacity_protocol import IJobCapacity
from .contract_job_cleanup_protocol import IJobCleanup
from .contract_job_event_protocol import IJobEventPublisher
from .contract_job_lifecycle_protocol import IJobLifecycle
from .contract_job_monitor_protocol import IJobMonitor
from .contract_job_protocol import JobSchedulerProtocol
from .taxonomy_job_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
)
from .taxonomy_job_event import JobEvent

__all__ = [
    "IJobAggregate",
    "IJobCancellation",
    "IJobCapacity",
    "IJobCleanup",
    "IJobEventPublisher",
    "IJobLifecycle",
    "IJobMonitor",
    "JobSchedulerProtocol",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_TIMED_OUT",
    "JobEvent",
]
