"""Capability: Job event publisher (logging adapter).

Implements IJobEventPublisher. This is an external-adaptation capability,
not a utility, because it implements a contract and performs I/O via logging.
"""

from __future__ import annotations

import logging

from modules.shared.src.job.contract_job_event_protocol import IJobEventPublisher
from modules.shared.src.job.taxonomy_job_event import JobEvent


class JobLoggingEventPublisher(IJobEventPublisher):
    def __init__(self, logger_name: str = "BlenderMCPServer") -> None:
        self._logger = logging.getLogger(logger_name)

    def emit(self, event: JobEvent) -> None:
        self._logger.info(
            "Job event: %s job=%s state=%s op=%s",
            event.event_type,
            event.job_id,
            event.state_after,
            event.operation_type,
        )

    def __repr__(self) -> str:
        return "<JobLoggingEventPublisher>"
