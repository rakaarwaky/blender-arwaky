"""VSE feature module — AES implementation for Wave 3."""

from .agent_vse_orchestrator import VseOrchestrator
from .root_vse_container import VseContainer, create_vse_feature

__all__ = [
    "VseContainer",
    "VseOrchestrator",
    "create_vse_feature",
]
