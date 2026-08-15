"""Composition root for the Animation AES feature."""

from __future__ import annotations

from modules.animation.src.agent_animation_orchestrator import AnimationOrchestrator
from modules.animation.src.capabilities_animation_executor import AnimationExecutor


class AnimationContainer:
    """Wire the injected gateway executor to the Animation agent."""

    def __init__(self, code_executor: object) -> None:
        self._orchestrator = AnimationOrchestrator(AnimationExecutor(code_executor))

    @property
    def aggregate(self) -> AnimationOrchestrator:
        return self._orchestrator


def create_animation_feature(code_executor: object) -> AnimationOrchestrator:
    """Create the fully wired Animation feature aggregate."""
    return AnimationContainer(code_executor).aggregate
