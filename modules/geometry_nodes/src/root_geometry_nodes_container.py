"""Composition root for the Geometry Nodes AES feature."""

from __future__ import annotations

from modules.geometry_nodes.src.agent_geometry_nodes_orchestrator import GeometryNodesOrchestrator
from modules.geometry_nodes.src.capabilities_geometry_nodes_executor import GeometryNodesExecutor


class GeometryNodesContainer:
    """Wire the injected gateway executor to the Geometry Nodes agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = GeometryNodesOrchestrator(GeometryNodesExecutor(code_executor))

    @property
    def aggregate(self) -> GeometryNodesOrchestrator:
        return self._orchestrator


def create_geometry_nodes_feature(code_executor: object) -> GeometryNodesOrchestrator:
    """Create the fully wired Geometry Nodes feature aggregate."""
    return GeometryNodesContainer(code_executor).aggregate
