"""Server contract — execution queue protocol interface.

Defines the behavior for serialized execution queue that prevents
concurrent bpy access. Implemented by Capabilities layer.
"""

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_server_vo import ExecutionResult


class IExecutionQueueProtocol(ABC):
    """Protocol for FIFO execution queue with depth limit and wait timeout.

    Serializes requests to prevent concurrent bpy access in Blender's
    single-threaded environment.
    """

    @abstractmethod
    async def enqueue(
        self,
        request_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Add item to queue. Raises QueueFullError if depth limit exceeded.

        Returns request_id after successful enqueue.
        """
        ...

    @abstractmethod
    async def dequeue(self) -> str | None:
        """Remove and return the next request_id from the queue.

        Returns None if queue is empty.
        """
        ...

    @abstractmethod
    async def wait_for_completion(
        self,
        request_id: str,
        timeout_ms: float | None = None,
    ) -> ExecutionResult:
        """Wait for a queued item to be processed and return result.

        Raises QueueTimeoutError if wait exceeds timeout_ms (or config default).
        """
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        """Return current queue depth."""
        ...
