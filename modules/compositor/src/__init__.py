"""Compositor feature module — AES implementation for Wave 3."""

from .agent_compositor_orchestrator import CompositorOrchestrator
from .root_compositor_container import CompositorContainer, create_compositor_feature

__all__ = [
    "CompositorContainer",
    "CompositorOrchestrator",
    "create_compositor_feature",
]
