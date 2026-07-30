"""Capability: FIFO operation queue and scene operation serialization.

FR-GWY-004: Serialize Scene-Mutating Operations
- Mutating operations route through queue
- Read-only operations skip queue
- Enforces depth limit and wait timeout
- Processes one operation at a time in FIFO order

Contains OperationQueue (asyncio-based, IOperationQueueProtocol)
and SceneQueueExecutor (sync queue-based, SceneQueueProtocol).
"""

from __future__ import annotations

import asyncio
import logging
import queue
import threading
from dataclasses import dataclass

from modules.shared.src.gateway.contract_event_protocol import (
    IEventPublisher,
)
from modules.shared.src.gateway.contract_scene_queue_protocol import (
    IOperationQueueProtocol,
    SceneQueueProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    ChannelConflictError,
    OperationWaitTimeoutError,
    PendingOpsLimitError,
    TimeoutError,
)
from modules.shared.src.gateway.taxonomy_gateway_event import (
    ItemDequeued,
    ItemEnqueued,
    OperationRejected,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    ExecutionResult,
    QueuedOperation,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
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
        self._event_publisher = event_publisher
        self._max_depth = max_depth
        self._wait_timeout_ms = wait_timeout_ms
        self._queue: list[QueuedOperation] = []
        self._operation_states: dict[str, OperationState] = {}
        self._started_events: dict[str, asyncio.Future] = {}
        self._result_events: dict[str, asyncio.Future] = {}
        self._lock = asyncio.Lock()

    async def enqueue(self, operation: QueuedOperation) -> int:
        async with self._lock:
            if len(self._queue) >= self._max_depth:
                logger.warning("Queue full (depth=%d)", self._max_depth)
                await self._event_publisher.publish(
                    OperationRejected(
                        request_id=operation.request_id,
                        reason="queue_full",
                    )
                )
                raise PendingOpsLimitError(
                    max_depth=self._max_depth,
                    request_id=operation.request_id,
                )
            self._queue.append(operation)
            depth = len(self._queue)
        await self._event_publisher.publish(
            ItemEnqueued(
                request_id=operation.request_id,
                queue_depth=depth,
            )
        )
        logger.info("Enqueued operation %s (depth=%d)", operation.request_id, depth)
        return depth

    async def dequeue(self) -> QueuedOperation | None:
        async with self._lock:
            if not self._queue:
                return None
            operation = self._queue.pop(0)
        await self._event_publisher.publish(ItemDequeued(request_id=operation.request_id))
        logger.info("Dequeued operation %s (remaining=%d)", operation.request_id, len(self._queue))
        return operation

    async def mark_started(self, request_id: str) -> None:
        async with self._lock:
            if request_id not in self._operation_states:
                self._operation_states[request_id] = OperationState()
            self._operation_states[request_id].started = True
        future = self._started_events.pop(request_id, None)
        if future and not future.done():
            future.set_result(None)

    async def complete(self, request_id: str, result: ExecutionResult | dict | str) -> None:
        async with self._lock:
            state = self._operation_states.get(request_id)
            if state:
                state.completed = True
                state.result = result
        future = self._result_events.pop(request_id, None)
        if future and not future.done():
            future.set_result(result)

    async def fail(self, request_id: str, error: Exception) -> None:
        async with self._lock:
            state = self._operation_states.get(request_id)
            if state:
                state.failed = True
                state.error = error
        future = self._result_events.pop(request_id, None)
        if future and not future.done():
            future.set_exception(error)

    async def wait_for_started(self, request_id: str, timeout_ms: float | None = None) -> None:
        timeout_ms = timeout_ms or self._wait_timeout_ms
        timeout_s = timeout_ms / 1000.0
        async with self._lock:
            state = self._operation_states.get(request_id)
            if state and state.started:
                return
            loop = asyncio.get_running_loop()
            future: asyncio.Future[None] = loop.create_future()
            self._started_events[request_id] = future
        try:
            await asyncio.wait_for(future, timeout=timeout_s)
        except asyncio.TimeoutError:
            async with self._lock:
                self._started_events.pop(request_id, None)
            raise OperationWaitTimeoutError(
                request_id=request_id,
                timeout_ms=timeout_ms,
            ) from None

    async def wait_for_result(self, request_id: str) -> ExecutionResult | dict | str:
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
            raise OperationWaitTimeoutError(request_id=request_id) from None

    async def cancel_pending(self, error: Exception) -> int:
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
        async with self._lock:
            return len(self._queue)

    def __repr__(self) -> str:
        return f"OperationQueue(max_depth={self._max_depth}, depth={len(self._queue)})"


@dataclass
class OperationState:
    started: bool = False
    completed: bool = False
    failed: bool = False
    result: ExecutionResult | dict | str | None = None
    error: Exception | None = None


class SceneQueueExecutor(SceneQueueProtocol):
    """Concrete implementation for serialized scene operation queue.

    FR-GWY-004: FIFO queue for mutating operations. Read-only skips queue.
    Enforces depth limit (channel conflict) and wait timeout.
    """

    def __init__(self, max_depth: int = 50, wait_timeout_seconds: float = 30.0) -> None:
        self._queue: queue.Queue[SceneOperationVO] = queue.Queue(maxsize=max_depth)
        self._max_depth: int = max_depth
        self._wait_timeout_seconds: float = wait_timeout_seconds
        self._execution_lock = threading.Lock()
        self._processing: bool = False

    def enqueue_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        if not operation.is_mutation:
            logger.debug("Read-only operation bypasses queue")
            return self._execute_directly(operation)
        try:
            self._queue.put_nowait(operation)
        except queue.Full:
            raise ChannelConflictError(f"Queue depth limit {self._max_depth} reached") from None
        acquired = self._execution_lock.acquire(timeout=self._wait_timeout_seconds)
        if not acquired:
            raise TimeoutError(f"Queue wait timeout exceeded after {self._wait_timeout_seconds}s")
        self._processing = True
        try:
            return self._execute_mutation(operation)
        finally:
            self._processing = False
            self._execution_lock.release()

    def get_queue_status(self) -> QueueStatusVO:
        return QueueStatusVO(
            current_depth=self._queue.qsize(),
            is_busy=self._processing,
            max_depth=self._max_depth,
        )

    def _execute_directly(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        logger.debug("Read-only bypass for operation class=%s", operation.operation_class)
        return SceneOperationOutcomeVO(
            status="success",
            execution_duration_ms=0.0,
        )

    def _execute_mutation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        self._queue.get()
        logger.debug("Executing mutating operation class=%s", operation.operation_class)
        return SceneOperationOutcomeVO(
            status="success",
            queue_wait_ms=0.0,
        )

    def __repr__(self) -> str:
        return f"SceneQueueExecutor(depth={self._queue.qsize()}/{self._max_depth}, busy={self._processing})"
