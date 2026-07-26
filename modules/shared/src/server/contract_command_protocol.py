"""Contract: Command dispatch protocol for Blender operations.

Implemented by Capabilities layer (BlenderCommandAdapter).
Per FR-SRV-003: Send Blender Commands via TCP socket with timeout enforcement
and FIFO queue serialization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ActionName
from .taxonomy_server_error import (
    CommandTimeoutError,
    QueueFullError,
    QueueTimeoutError,
)
from .taxonomy_server_event import (
    CommandDispatched,
    ItemDequeued,
    ItemEnqueued,
)
from .taxonomy_server_vo import CommandResult, ExecutionResult


class IBlenderCommandProtocol(ABC):
    """Protocol for dispatching named commands and managing execution queue.

    Implemented by Capabilities layer (BlenderCommandAdapter).
    Each command is routed through TCP socket with configurable timeout
    enforcement per FR-SRV-003, with FIFO queue serialization.
    """

    @abstractmethod
    async def send_command(
        self,
        action: ActionName,
        params: dict | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        """Dispatch a named command to Blender addon.

        Success: Returns CommandResult with status='success', data from JSON response,
                 event=CommandDispatched(action, execution_time_ms)
        Failure: Raises CommandTimeoutError if response exceeds configured timeout
        Event: CommandDispatched(action, execution_time_ms)
        """
        ...

    @abstractmethod
    async def enqueue(
        self,
        request_id: str,
        payload: dict,
    ) -> int:
        """Add item to queue. Returns current queue depth.

        Success: Returns queue depth after enqueue; event=ItemEnqueued(request_id, queue_depth)
        Failure: Raises QueueFullError if max_depth exceeded
        Event: ItemEnqueued(request_id, queue_depth)
        """
        ...

    @abstractmethod
    async def dequeue(self) -> str | None:
        """Remove and return the next request_id from the queue.

        Success: Returns request_id; event=ItemDequeued(request_id)
        Failure: None (returns None if queue is empty — not an error)
        Event: ItemDequeued(request_id)
        """
        ...

    @abstractmethod
    async def wait_for_completion(
        self,
        request_id: str,
        timeout_ms: float | None = None,
    ) -> ExecutionResult:
        """Wait for a queued item to be processed and return result.

        Success: Returns ExecutionResult with status from queue processing
        Failure: Raises QueueTimeoutError if wait exceeds timeout_ms
        Event: None (internal queue detail)
        """
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        """Return current queue depth.

        Success: Returns queue depth as int
        Failure: Raises ConnectionClosedError if connection lost
        Event: None (pure query)
        """
        ...
