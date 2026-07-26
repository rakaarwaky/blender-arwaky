"""Contract: Operation queue protocol for serialized execution.

Implemented by operation queue capability. Owned and driven by Agent layer.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_server_vo import ExecutionResult, QueuedOperation


class IOperationQueueProtocol(ABC):
    """FIFO operation queue with depth limits and cancellation support."""

    @abstractmethod
    async def enqueue(self, operation: QueuedOperation) -> int:
        """Add operation to queue. Returns current queue depth.

        Raises TooManyPendingOperationsError if max_depth exceeded.
        Emits ItemEnqueued event on success.
        """
        ...

    @abstractmethod
    async def dequeue(self) -> QueuedOperation | None:
        """Remove and return the next operation from the queue (FIFO).

        Returns None if queue is empty — not an error condition.
        Emits ItemDequeued event on success.
        """
        ...

    @abstractmethod
    async def mark_started(self, request_id: str) -> None:
        """Mark an operation as started by request_id."""
        ...

    @abstractmethod
    async def complete(
        self,
        request_id: str,
        result: ExecutionResult | dict | str,
    ) -> None:
        """Mark an operation as completed with its result."""
        ...

    @abstractmethod
    async def fail(self, request_id: str, error: Exception) -> None:
        """Mark an operation as failed with the error."""
        ...

    @abstractmethod
    async def wait_for_started(
        self,
        request_id: str,
        timeout_ms: float,
    ) -> None:
        """Wait until the operation with request_id has started.

        Raises OperationWaitTimeoutError if timeout expires before start.
        """
        ...

    @abstractmethod
    async def wait_for_result(
        self,
        request_id: str,
    ) -> ExecutionResult | dict | str:
        """Wait for the operation result to complete.

        Returns the ExecutionResult or result dict when available.
        Raises OperationWaitTimeoutError if the operation times out.
        """
        ...

    @abstractmethod
    async def cancel_pending(self, error: Exception) -> int:
        """Cancel all pending operations with the given error.

        Returns the number of operations cancelled.
        """
        ...

    @abstractmethod
    async def cancel_by_task_id(self, task_id: str, error: Exception) -> bool:
        """Cancel a specific operation by task_id.

        Returns True if an operation was cancelled, False otherwise.
        """
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        """Return current queue depth."""
        ...
