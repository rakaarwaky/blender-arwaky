"""Aggregate contract for the job feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_job_cancel_protocol import JobCancelProtocol
from .contract_job_capacity_protocol import JobCapacityProtocol
from .contract_job_cleanup_protocol import JobCleanupProtocol
from .contract_job_monitor_protocol import JobMonitorProtocol
from .contract_job_tracker_protocol import JobTrackerProtocol

__all__ = [
    "JobCancelProtocol",
    "JobCapacityProtocol",
    "JobCleanupProtocol",
    "JobMonitorProtocol",
    "JobTrackerProtocol",
]
