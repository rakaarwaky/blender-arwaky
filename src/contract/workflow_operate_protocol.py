"""
Contract: Workflow Protocol (AES _protocol suffix).
"""

from abc import ABC, abstractmethod

from taxonomy import Prompt, SuccessFlag


class WorkflowProtocol(ABC):
    """Business logic interface for complex multi-step workflows."""

    @abstractmethod
    async def create_basic_scene(self, prompt: Prompt) -> SuccessFlag:
        """Create a basic scene."""
        pass
