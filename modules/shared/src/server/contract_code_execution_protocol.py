"""Contract: Protocol for executing Python code in Blender.

Implemented by Capabilities that handle code validation,
execution queue, and result formatting.
AES Protocol layer — depends only on Taxonomy.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import Prompt
from .taxonomy_server_vo import ExecutionResult


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender."""

    @abstractmethod
    async def execute_blender_code(self, code: Prompt) -> Prompt:
        """Execute arbitrary Python code in Blender and return result."""
        pass

    @abstractmethod
    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution. Returns task_id and status."""
        pass

    @abstractmethod
    async def poll_task_result(self, task_id: str, request_id: str) -> ExecutionResult:
        """Poll async task status and final result."""
        pass
