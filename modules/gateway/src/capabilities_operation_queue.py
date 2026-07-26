"""Capability: FIFO operation queue with depth limits and cancellation support.

Implements IOperationQueueProtocol — owned and driven by Agent layer
orchestrator for serialized scene-mutating operations. Supports
enqueue, dequeue, completion/failure tracking, and cancellation.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass

from modules.gateway.src import (
    IEventPublisher,
    IOperationQueueProtocol,
    OperationRejected,
    OperationWaitTimeoutError,
    TooManyPendingOperationsError,
)

from modules.gateway.src import (
    ItemDequeued,
    ItemEnqueued,
    ExecutionResult,
    QueuedOperation,
)

logger = logging.getLogger("BlenderMCPServer")


class OperationQueue(IOperationQueueProtocol):
    """FIFO operation queue with depth limits and cancellation support.

    Thread-safe under asyncio (uses asyncio.Lock). Enforces max_depth,
    emits ItemEnqueued/ItemDequeued/OperationRejected events, and
    supports cancellation by request_id and task_id.
    """

    def __init__(
        self,
        event_publisher: IEventPublisher,
        max_depth: int = 50,
        wait_timeout_ms: float = 10_000.0,
    ) -> None:
        """Initialize operation queue.

        Args:
            event_publisher: Event bus for emitting queue events.
            max_depth: Maximum number of pending operations.
            wait_timeout_ms: Default timeout for waiting on operations.
        """
        self._event_publisher = event_publisher
        self._max_depth = max_depth
        self._wait_timeout_ms = wait_timeout_ms

        # Queue storage
        self._queue: list[QueuedOperation] = []

        # Operation state tracking
        self._operation_states: dict[str, "OperationState"] = {}
        self._started_events: dict[str, asyncio.Future] = {}
        self._result_events: dict[str, asyncio.Future] = {}

        self._lock = asyncio.Lock()

    async def enqueue(self, operation: QueuedOperation) -> int:
        """Add operation to queue. Raises TooManyPendingOperationsError if full.

        Args:
            operation: The queued operation to enqueue.

        Returns:
            Current queue depth after enqueue.

        Raises:
            TooManyPendingOperationsError: If max_depth exceeded.
        """
        async with self._lock:
            if len(self._queue) >= self._max_depth:
                logger.warning("Queue full (depth=%d)", self._max_depth)
                await self._event_publisher.publish(
                    OperationRejected(
                        request_id=operation.request_id,
                        reason="queue_full",
                    )
                )
                raise TooManyPendingOperationsError(
                    max_depth=self._max_depth,
                    request_id=operation.request_id,
                )

            self._queue.append(operation)
            depth = len(self._queue)

        # Emit event outside lock
        await self._event_publisher.publish(ItemEnqueued(
            request_id=operation.request_id,
            queue_depth=depth,
        ))

        logger.info("Enqueued operation %s (depth=%d)", operation.request_id, depth)
        return depth

    async def dequeue(self) -> QueuedOperation | None:
        """Remove and return the next operation from the queue (FIFO).

        Returns:
            The next QueuedOperation, or None if queue is empty.
        """
        async with self._lock:
            if not self._queue:
                return None
            operation = self._queue.pop(0)

        # Emit event outside lock
        await self._event_publisher.publish(ItemDequeued(request_id=operation.request_id))

        logger.info("Dequeued operation %s (remaining=%d)", operation.request_id, len(self._queue))
        return operation

    async def mark_started(self, request_id: str) -> None:
        """Mark an operation as started by request_id."""
        async with self._lock:
            if request_id not in self._operation_states:
                self._operation_states[request_id] = OperationState()
            self._operation_states[request_id].started = True

        # Signal the future waiter
        future = self._started_events.pop(request_id, None)
        if future and not future.done():
            future.set_result(None)

    async def complete(self, request_id: str, result: ExecutionResult | dict | str) -> None:
        """Mark an operation as completed with its result.

        Args:
            request_id: The request ID to mark complete.
            result: The execution result.
        """
        async with self._lock:
            state = self._operation_states.get(request_id)
            if state:
                state.completed = True
                state.result = result

        # Signal the result waiter
        future = self._result_events.pop(request_id, None)
        if future and not future.done():
            future.set_result(result)

    async def fail(self, request_id: str, error: Exception) -> None:
        """Mark an operation as failed with the error.

        Args:
            request_id: The request ID to mark failed.
            error: The failure exception.
        """
        async with self._lock:
            state = self._operation_states.get(request_id)
            if state:
                state.failed = True
                state.error = error

        # Signal the result waiter with error
        future = self._result_events.pop(request_id, None)
        if future and not future.done():
            future.set_exception(error)

    async def wait_for_started(self, request_id: str, timeout_ms: float | None = None) -> None:
        """Wait until the operation with request_id has started.

        Raises OperationWaitTimeoutError if timeout expires before start.

        Args:
            request_id: The request ID to wait for.
            timeout_ms: Timeout in milliseconds. Uses default if None.
        """
        timeout_ms = timeout_ms or self._wait_timeout_ms
        timeout_s = timeout_ms / 1000.0

        async with self._lock:
            state = self._operation_states.get(request_id)
            if state and state.started:
                return  # Already started

            # Create future to wait on
            loop = asyncio.get_running_loop()
            future: asyncio.Future[None] = loop.create_future()
            self._started_events[request_id] = future

        try:
            await asyncio.wait_for(future, timeout=timeout_s)
        except asyncio.TimeoutError:
            # Remove from tracking
            async with self._lock:
                self._started_events.pop(request_id, None)
            raise OperationWaitTimeoutError(
                request_id=request_id,
                timeout_ms=timeout_ms,
            )

    async def wait_for_result(self, request_id: str) -> ExecutionResult | dict | str:
        """Wait for the operation result to complete.

        Returns:
            The ExecutionResult or result dict when available.

        Raises:
            OperationWaitTimeoutError: If the operation times out.
        """
        async with self._lock:
            state = self._operation_states.get(request_id)
            if state and state.completed:
                return state.result
            if state and state.failed:
                raise state.error

            loop = asyncio.get_running_loop()
            future: asyncio.Future[ExecutionResult | dict | str] = loop.create_future()
            self._result_events[request_id] = future

        try:
            return await future
        except asyncio.TimeoutError:
            raise OperationWaitTimeoutError(request_id=request_id)

    async def cancel_pending(self, error: Exception) -> int:
        """Cancel all pending operations with the given error.

        Args:
            error: The error to assign to cancelled operations.

        Returns:
            Number of operations cancelled.
        """
        async with self._lock:
            cancelled = 0
            remaining = []
            for op in self._queue:
                state = self._operation_states.get(op.request_id)
                if state and state.started:
                    remaining.append(op)
                else:
                    if state:
                        state.error = error
                    cancelled += 1

            self._queue = remaining

        return cancelled

    async def cancel_by_task_id(self, task_id: str, error: Exception) -> bool:
        """Cancel a specific operation by task_id.

        Args:
            task_id: The task ID to cancel.
            error: The error to assign.

        Returns:
            True if an operation was cancelled, False otherwise.
        """
        async with self._lock:
            for i, op in enumerate(self._queue):
                if op.task_id == task_id:
                    state = self._operation_states.get(op.request_id)
                    if state:
                        state.error = error
                    self._queue.pop(i)
                    return True
        return False

    async def get_depth(self) -> int:
        """Return current queue depth."""
        async with self._lock:
            return len(self._queue)

    def __repr__(self) -> str:
        return f"OperationQueue(max_depth={self._max_depth}, depth={len(self._queue)})"


@dataclass
class OperationState:
    """Internal mutable state for a queued operation."""

    started: bool = False
    completed: bool = False
    failed: bool = False
    result: ExecutionResult | dict | str | None = None
    error: Exception | None = None

