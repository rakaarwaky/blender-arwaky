"""Composition root for the VSE AES feature."""

from __future__ import annotations

from modules.vse.src.agent_vse_orchestrator import VseOrchestrator
from modules.vse.src.capabilities_vse_executor import VseExecutor


class VseContainer:
    """Wire the injected gateway executor to the VSE agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = VseOrchestrator(VseExecutor(code_executor))

    @property
    def aggregate(self) -> VseOrchestrator:
        return self._orchestrator


def create_vse_feature(code_executor: object) -> VseOrchestrator:
    """Create the fully wired VSE feature aggregate."""
    return VseContainer(code_executor).aggregate
