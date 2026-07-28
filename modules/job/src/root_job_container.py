# modules/job/src/root_job_container.py
from __future__ import annotations

import logging
import time
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import Timestamp
from modules.shared.src.job.contract_job_protocol import (
    ICancellationSignaler,
    IJobEventPublisher,
)
from modules.shared.src.job.taxonomy_job_vo import JobPolicy

from .agent_job_orchestrator import JobOrchestrator
from .capabilities_job_registry import InMemoryJobRegistry

logger = logging.getLogger("BlenderMCPServer")


class JobContainer:
    """Dependency injection container for the job feature module."""

    def __init__(
        self,
        policy: JobPolicy | None = None,
        cancellation_signaler: ICancellationSignaler | None = None,
        event_publisher: IJobEventPublisher | None = None,
        clock: Callable[[], Timestamp] | None = None,
    ) -> None:
        self._policy = policy or JobPolicy()
        self._cancellation_signaler = cancellation_signaler
        self._event_publisher = event_publisher
        self._clock = clock

        self._orchestrator: JobOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        if self._wired:
            return

        logger.info("Wiring job feature module")

        clock = self._clock or (lambda: Timestamp(time.time()))

        registry = InMemoryJobRegistry(
            policy=self._policy,
            clock=clock,
            cancellation_signaler=self._cancellation_signaler,
            event_publisher=self._event_publisher,
        )

        self._orchestrator = JobOrchestrator(registry)
        self._wired = True

        logger.info("Job feature module wired successfully")

    @property
    def agent(self) -> JobOrchestrator:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("JobContainer not wired — call wire() first")
        return self._orchestrator


def create_job_feature(
    policy: JobPolicy | None = None,
    cancellation_signaler: ICancellationSignaler | None = None,
    event_publisher: IJobEventPublisher | None = None,
    clock: Callable[[], Timestamp] | None = None,
) -> JobOrchestrator:
    container = JobContainer(
        policy=policy,
        cancellation_signaler=cancellation_signaler,
        event_publisher=event_publisher,
        clock=clock,
    )
    container.wire()
    return container.agent
