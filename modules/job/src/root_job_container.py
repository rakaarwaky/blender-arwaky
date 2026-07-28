"""Root: Job feature composition container.

Wires the job orchestrator (self-contained lifecycle state machine) and
bootstraps the job module. The JobOrchestrator owns task state directly and
delegates to no external capabilities.

This file is the composition root for the job feature.
"""

from __future__ import annotations

import logging

from .agent_job_orchestrator import JobOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class JobContainer:
    """Dependency injection container for the job feature module."""

    def __init__(self, max_active: int = 100) -> None:
        self._max_active = max_active
        self._orchestrator: JobOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the job orchestrator."""
        if self._wired:
            return

        logger.info("Wiring job feature module")

        self._orchestrator = JobOrchestrator(max_active=self._max_active)

        self._wired = True
        logger.info("Job feature module wired successfully")

    @property
    def agent(self) -> JobOrchestrator:
        """Return the assembled job orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("JobContainer not wired — call wire() first")
        return self._orchestrator


def create_job_feature(max_active: int = 100) -> JobOrchestrator:
    """Factory function to create and wire the job feature module."""
    container = JobContainer(max_active=max_active)
    container.wire()
    return container.agent
