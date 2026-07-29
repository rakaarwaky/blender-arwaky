"""Utility: Job event emitter (default implementation).

Wires JobEvent through Python logging for decoupled emission.
Serves as the default IJobEventPublisher when no external bus is available.
"""
from __future__ import annotations

import logging

from modules.shared.src.job.contract_job_event_protocol import IJobEventPublisher
from modules.shared.src.job.taxonomy_job_event import JobEvent

logger = logging.getLogger("BlenderMCPServer")


class JobEventEmitter(IJobEventPublisher):
    """Default event emitter that delegates to Python logging."""

    def __init__(self, logger_name: str = "BlenderMCPServer") -> None:
        self._logger = logging.getLogger(logger_name)

    def emit(self, event: JobEvent) -> None:
        """Emit a job event through structured logging.

        Maintains backward compatibility with the previous _emit() pattern.
        """
        self._logger.info(
            "Job event: %s job=%s state=%s op=%s",
            event.event_type,
            event.job_id,
            event.state_after,
            event.operation_type,
        )
