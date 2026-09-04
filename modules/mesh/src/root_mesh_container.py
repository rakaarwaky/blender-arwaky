"""Composition root for the Mesh AES feature."""

from __future__ import annotations

from modules.mesh.src.agent_mesh_orchestrator import MeshOrchestrator
from modules.mesh.src.capabilities_mesh_executor import MeshExecutor


class MeshContainer:
    """Wire the injected gateway executor to the Mesh agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = MeshOrchestrator(MeshExecutor(code_executor))

    @property
    def aggregate(self) -> MeshOrchestrator:
        return self._orchestrator


def create_mesh_feature(code_executor: object) -> MeshOrchestrator:
    """Create the fully wired Mesh feature aggregate."""
    return MeshContainer(code_executor).aggregate
