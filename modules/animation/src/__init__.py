"""Animation feature module — AES implementation for Wave 2."""

from .agent_animation_orchestrator import AnimationOrchestrator
from .root_animation_container import AnimationContainer, create_animation_feature

__all__ = [
    "AnimationContainer",
    "AnimationOrchestrator",
    "create_animation_feature",
]
