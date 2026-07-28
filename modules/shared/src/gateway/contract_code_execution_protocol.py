"""Gateway domain contract: code execution protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-GWY-005: Execute raw Python code with security validation and bounded output.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import CodeExecutionOutcomeVO, CodeExecutionVO


class CodeExecutionProtocol(ABC):
    """Protocol interface for raw Python code execution with security checks."""

    @abstractmethod
    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        """Execute raw Python code in Blender with security validation.

        FR-GWY-005: Validates code via security policy feature before transport.
        Enforces execution timeout. Truncates oversized output with indicator.
        Does not manage background task lifecycle.
        """
        ...


from .taxonomy_gateway_vo import ExecutionResult, TaskStatus


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender and managing async task lifecycle.

    All methods use explicit typed errors — no bare strings.
    Query methods return typed results; state transitions raise on failure.
    """

    @abstractmethod
    async def execute_blender_code(self, code: str, request_id: str | None = None) -> ExecutionResult:
        """Execute arbitrary Python code in Blender and return result.

        Success: Returns ExecutionResult with status='success'
        Failure: Raises SecurityViolationError (blocked patterns), ExecutionTimeoutError,
                 or any Blender execution exception
        Event: CodeExecuted(request_id, execution_time_ms) on success;
                 CodeExecutionFailed(request_id, error_type, message) on failure
        """
        ...

    @abstractmethod
    async def execute_task(self, task_id: str, code: str, request_id: str | None = None) -> ExecutionResult:
        """Execute code for an existing task. Internal use by queue worker."""
        ...

    @abstractmethod
    def create_task(self, request_id: str | None = None) -> str:
        """Create a new pending task. Returns the new task_id.

        Success: Returns task_id; event=TaskCreated(task_id, request_id)
        """
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> TaskStatus:
        """Get task status.

        Success: Returns TaskStatus with current state
        Failure: Raises TaskNotFoundError if not found or expired
        Event: None (pure query)
        """
        ...

    @abstractmethod
    async def poll_task_result(self, task_id: str, request_id: str | None = None) -> TaskStatus:
        """Poll async task status and final result.

        Success: Returns TaskStatus with current state and optional ExecutionResult
        Failure: Raises TaskNotFoundError if not found or expired
        Event: TaskCompleted(task_id, execution_time_ms) on success;
                 TaskFailed(task_id, error_type, message) on error
        """
        ...

    @abstractmethod
    async def cancel_async_task(self, task_id: str, request_id: str | None = None) -> TaskStatus:
        """Cancel a pending or running task.

        Success: Returns TaskStatus with updated state
        - If pending: removes from queue, marks cancelled, emits TaskCancelled
        - If running: attempts asyncio cancellation, sets cancel_requested=True
        Failure: Raises TaskNotFoundError if not found
        Event: TaskCancelled(task_id) on successful cancellation
        """
        ...

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired tasks beyond retention window.

        Success: Returns number of tasks removed.
        Called on task creation, polling, and queue worker cycles.
        """
        ...
