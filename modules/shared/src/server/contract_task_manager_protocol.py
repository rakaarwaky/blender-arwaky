"""Server contract — task manager protocol interface.

Defines the behavior for async task lifecycle management.
Implemented by Capabilities layer.
"""

from abc import ABC, abstractmethod

from .taxonomy_server_vo import ExecutionResult, TaskStatus


class ITaskManagerProtocol(ABC):
    """Protocol for async task lifecycle management.

    Tracks task states: pending → running → success/error/timeout/cancel.
    Enforces TTL expiry and max task limits.
    """

    @abstractmethod
    def create_task(self, request_id: str) -> str:
        """Create a new pending task. Returns task_id."""
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> TaskStatus:
        """Get task status. Raises TaskNotFoundError if not found or expired."""
        ...

    @abstractmethod
    def mark_running(self, task_id: str) -> None:
        """Transition task to running state."""
        ...

    @abstractmethod
    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        """Transition task to success state with result."""
        ...

    @abstractmethod
    def mark_error(self, task_id: str, error: str) -> None:
        """Transition task to error state."""
        ...

    @abstractmethod
    def mark_timeout(self, task_id: str) -> None:
        """Transition task to timeout state."""
        ...

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Returns True if cancelled, False if already running."""
        ...
