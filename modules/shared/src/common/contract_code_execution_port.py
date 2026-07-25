"""Common contract: code execution port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_core_vo import Prompt


class ContractCodeExecutionPort(ABC):
    """Port interface for executing Python code in Blender."""

    @abstractmethod
    async def execute_blender_code(self, code: Prompt) -> Prompt:
        """Execute arbitrary Python code in Blender and return result."""
        pass
