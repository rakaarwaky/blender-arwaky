"""Contract: Protocol for executing Python code in Blender.

Implemented by Capabilities that handle code validation,
execution queue, and result formatting.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import Prompt
from .taxonomy_server_error import (
    CodeValidationError,
    ExecutionTimeoutError,
    TaskNotFoundError,
)
from .taxonomy_server_event import (
    CodeExecuted,
    CodeExecutionFailed,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskStarted,
    TaskTimedOut,
)
from .taxonomy_server_vo import ExecutionResult, TaskStatus


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender and managing async task lifecycle.

    All methods use explicit typed errors — no bare strings.
    Query methods return typed results; state transitions raise on failure.
    """

    @abstractmethod
    async def execute_blender_code(self, code: Prompt) -> ExecutionResult:
        """Execute arbitrary Python code in Blender and return result.

        Success: Returns ExecutionResult with status='success', data from execution
        Failure: Raises CodeValidationError (blocked patterns), ExecutionTimeoutError,
                 or any Blender execution exception
        Event: CodeExecuted(request_id, execution_time_ms) on success;
                 CodeExecutionFailed(request_id, error_type, message) on failure
        """
        ...

    @abstractmethod
    async def submit_async_task(self, code: Prompt, request_id: str) -> str:
        """Submit long-running code for async execution. Returns new TaskId.

        Success: Returns newly created TaskId; event=TaskCreated(task_id, request_id)
        Failure: Raises CodeValidationError (code contains blocked patterns)
        Event: TaskCreated(task_id, request_id)
        """
        ...

    @abstractmethod
    async def poll_task_result(self, task_id: str) -> ExecutionResult:
        """Poll async task status and final result.

        Success: Returns ExecutionResult (success or error) with event=TaskCompleted(task_id)
                 if task is in terminal state
        Failure: Raises TaskNotFoundError if task not found or expired
        Event: TaskCompleted(task_id, execution_time_ms) on success;
                 TaskFailed(task_id, error_type, message) on error
        """
        ...

    @abstractmethod
    def create_task(self, request_id: str) -> str:
        """Create a new pending task. Returns the new TaskId.

        Success: Returns TaskId; event=TaskCreated(task_id, request_id)
        Failure: Raises ExecutionTimeoutError if task creation exceeds deadline
        Event: TaskCreated(task_id, request_id)
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
    def mark_running(self, task_id: str) -> None:
        """Transition task to running state.

        Success: No return; event=TaskStarted(task_id)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskStarted(task_id)
        """
        ...

    @abstractmethod
    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        """Transition task to success state with result.

        Success: No return; event=TaskCompleted(task_id, execution_time_ms)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskCompleted(task_id, execution_time_ms)
        """
        ...

    @abstractmethod
    def mark_error(self, task_id: str, error_type: str, message: str) -> None:
        """Transition task to error state.

        Success: No return; event=TaskFailed(task_id, error_type, message)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskFailed(task_id, error_type, message)
        """
        ...

    @abstractmethod
    def mark_timeout(self, task_id: str) -> None:
        """Transition task to timeout state.

        Success: No return; event=TaskTimedOut(task_id)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskTimedOut(task_id)
        """
        ...

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Returns True if cancelled, False if already running.

        Success: Returns True (cancelled) or False (already running);
                 event=TaskCancelled(task_id) on successful cancellation
        Failure: Raises TaskNotFoundError if task not found; raises no exception on already-running
        Event: TaskCancelled(task_id)
        """
        ...
