"""Root: Job feature composition container.

Wires 5 capabilities to 5 protocols, assembles the agent.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import Timestamp
from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from modules.shared.src.job.taxonomy_job_vo import JobPolicy

from .agent_job_orchestrator import JobOrchestrator
from .capabilities_job_checker import JobCapacityChecker
from .capabilities_job_evaluator import JobCancellationEvaluator
from .capabilities_job_event_publisher import JobLoggingEventPublisher
from .capabilities_job_monitor import JobStatusMonitor
from .capabilities_job_repository import InMemoryJobLifecycleRepository
from .capabilities_job_resolver import JobCleanupResolver
from .capabilities_job_scheduler import JobSchedulerCapability

logger = logging.getLogger("BlenderMCPServer")


class JobContainer:
    def __init__(
        self,
        policy: JobPolicy | None = None,
        clock: Callable[[], Timestamp] | None = None,
    ) -> None:
        self._policy = policy or JobPolicy()
        self._clock = clock
        self._orchestrator: JobOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        if self._wired:
            return

        logger.info("Wiring job feature module")

        clock = self._clock or (lambda: Timestamp(time.time()))
        event_publisher = JobLoggingEventPublisher()

        lifecycle = InMemoryJobLifecycleRepository(
            policy=self._policy,
            clock=clock,
            event_publisher=event_publisher,
        )
        monitor = JobStatusMonitor()
        cancellation = JobCancellationEvaluator()
        cleanup = JobCleanupResolver()
        capacity = JobCapacityChecker()
        scheduler = JobSchedulerCapability()
        _ = scheduler


        self._orchestrator = JobOrchestrator(
            lifecycle=lifecycle,
            monitor=monitor,
            cancellation=cancellation,
            cleanup=cleanup,
            capacity=capacity,
            policy=self._policy,
            clock=clock,
        )
        self._wired = True
        logger.info("Job feature module wired: 5 capabilities composed")

    @property
    def agent(self) -> IJobAggregate:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("JobContainer not wired — call wire() first")
        return self._orchestrator


def create_job_feature(
    policy: JobPolicy | None = None,
    clock: Callable[[], Timestamp] | None = None,
) -> IJobAggregate:
    container = JobContainer(policy=policy, clock=clock)
    container.wire()
    return container.agent
