"""Physics feature module — AES implementation for Wave 3."""

from .agent_physics_orchestrator import PhysicsOrchestrator
from .root_physics_container import PhysicsContainer, create_physics_feature

__all__ = [
    "PhysicsContainer",
    "PhysicsOrchestrator",
    "create_physics_feature",
]
