"""Cross-cutting contract: workflow protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_core_vo import Prompt, SuccessFlag


class WorkflowProtocol(ABC):
    """Business logic interface for complex multi-step workflows."""

    @abstractmethod
    async def create_basic_scene(self, prompt: Prompt) -> SuccessFlag:
        """Create a basic scene."""
        pass