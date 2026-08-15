"""Composition root for the Rigging and Deformation AES feature."""

from __future__ import annotations

from modules.rigging.src.agent_rigging_orchestrator import RiggingOrchestrator
from modules.rigging.src.capabilities_rigging_executor import RiggingExecutor


class RiggingContainer:
    """Wire the injected gateway executor to the Rigging agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = RiggingOrchestrator(RiggingExecutor(code_executor))

    @property
    def aggregate(self) -> RiggingOrchestrator:
        return self._orchestrator


def create_rigging_feature(code_executor: object) -> RiggingOrchestrator:
    """Create the fully wired Rigging feature aggregate."""
    return RiggingContainer(code_executor).aggregate
