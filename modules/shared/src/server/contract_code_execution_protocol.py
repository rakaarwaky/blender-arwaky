"""Contract: Protocol for executing Python code in Blender.

Implemented by Capabilities that handle code validation,
execution queue, and result formatting.
AES Protocol layer — depends only on Taxonomy.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import Prompt
from .taxonomy_server_vo import ExecutionResult, TaskStatus


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender and managing async task lifecycle."""

    @abstractmethod
    async def execute_blender_code(self, code: Prompt) -> ExecutionResult:
        """Execute arbitrary Python code in Blender and return result."""
        pass

    @abstractmethod
    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution. Returns task_id and status."""
        pass

    @abstractmethod
    async def poll_task_result(self, task_id: str, request_id: str = "") -> ExecutionResult:
        """Poll async task status and final result."""
        pass

    @abstractmethod
    def create_task(self, request_id: str) -> str:
        """Create a new pending task. Returns task_id."""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> TaskStatus:
        """Get task status. Raises TaskNotFoundError if not found or expired."""
        pass

    @abstractmethod
    def mark_running(self, task_id: str) -> None:
        """Transition task to running state."""
        pass

    @abstractmethod
    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        """Transition task to success state with result."""
        pass

    @abstractmethod
    def mark_error(self, task_id: str, error: str) -> None:
        """Transition task to error state."""
        pass

    @abstractmethod
    def mark_timeout(self, task_id: str) -> None:
        """Transition task to timeout state."""
        pass

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Returns True if cancelled, False if already running."""
        pass

