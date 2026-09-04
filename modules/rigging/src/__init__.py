"""Rigging and deformation feature module — AES implementation for Wave 5."""

from .agent_rigging_orchestrator import RiggingOrchestrator
from .root_rigging_container import RiggingContainer, create_rigging_feature

__all__ = [
    "RiggingContainer",
    "RiggingOrchestrator",
    "create_rigging_feature",
]
