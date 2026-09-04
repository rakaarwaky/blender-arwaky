"""Composition root for the Compositor AES feature."""

from __future__ import annotations

from modules.compositor.src.agent_compositor_orchestrator import CompositorOrchestrator
from modules.compositor.src.capabilities_compositor_executor import CompositorExecutor


class CompositorContainer:
    """Wire the injected gateway executor to the Compositor agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = CompositorOrchestrator(CompositorExecutor(code_executor))

    @property
    def aggregate(self) -> CompositorOrchestrator:
        return self._orchestrator


def create_compositor_feature(code_executor: object) -> CompositorOrchestrator:
    """Create the fully wired Compositor feature aggregate."""
    return CompositorContainer(code_executor).aggregate
