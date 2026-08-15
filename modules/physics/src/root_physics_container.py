"""Composition root for the Physics AES feature."""

from __future__ import annotations

from modules.physics.src.agent_physics_orchestrator import PhysicsOrchestrator
from modules.physics.src.capabilities_physics_executor import PhysicsExecutor


class PhysicsContainer:
    """Wire the injected gateway executor to the Physics agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = PhysicsOrchestrator(PhysicsExecutor(code_executor))

    @property
    def aggregate(self) -> PhysicsOrchestrator:
        return self._orchestrator


def create_physics_feature(code_executor: object) -> PhysicsOrchestrator:
    """Create the fully wired Physics feature aggregate."""
    return PhysicsContainer(code_executor).aggregate
