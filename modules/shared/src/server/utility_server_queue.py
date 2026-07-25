"""Utility: FIFO execution queue for serialized Blender operations.

Stateless queue management with configurable depth limit and wait timeout.
Used to serialize requests due to Blender's single-threaded bpy constraint.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ..server.taxonomy_server_error import QueueFullError, QueueTimeoutError

logger = logging.getLogger("BlenderMCPServer")


@dataclass(frozen=True)
class QueueConfig:
    """Queue configuration parameters."""

    max_depth: int = 50
    wait_timeout_ms: float = 10000.0  # 10 seconds default


@dataclass
class QueueItem:
    """Single item in the execution queue."""

    request_id: str
    payload: dict[str, Any]
    enqueued_at: float = field(default_factory=time.monotonic)
    result: Any = None
    error: Exception | None = None


class ExecutionQueue:
    """FIFO execution queue with depth limit and wait timeout.

    Serializes requests to prevent concurrent bpy access.
    Rejects with QueueFullError when max_depth exceeded.
    Rejects with QueueTimeoutError when wait exceeds configured timeout.
    """

    def __init__(self, config: QueueConfig | None = None) -> None:
        self._config = config or QueueConfig()
        self._queue: list[QueueItem] = []
        self._lock = asyncio.Lock()

    async def enqueue(
        self,
        request_id: str,
        payload: dict[str, Any],
    ) -> QueueItem:
        """Add item to queue. Raises QueueFullError if depth limit exceeded.

        Returns the QueueItem after successful enqueue.
        """
        async with self._lock:
            if len(self._queue) >= self._config.max_depth:
                raise QueueFullError(
                    f"Queue full: {len(self._queue)}/{self._config.max_depth}"
                )

            item = QueueItem(request_id=request_id, payload=payload)
            self._queue.append(item)
            logger.info("Enqueued request %s (%d/%d)", request_id, len(self._queue), self._config.max_depth)
            return item

    async def dequeue(self) -> QueueItem | None:
        """Remove and return the next item from the queue.

        Returns None if queue is empty.
        """
        async with self._lock:
            if not self._queue:
                return None
            item = self._queue.pop(0)
            logger.info("Dequeued request %s (%d remaining)", item.request_id, len(self._queue))
            return item

    async def wait_for_completion(
        self,
        item: QueueItem,
        timeout_ms: float | None = None,
    ) -> Any:
        """Wait for a queued item to be processed and return result.

        Raises QueueTimeoutError if wait exceeds timeout_ms (or config default).
        Returns the result stored in the QueueItem.
        """
        timeout_ms = timeout_ms or self._config.wait_timeout_ms
        timeout_s = timeout_ms / 1000.0

        # Poll until item has a result or error
        deadline = time.monotonic() + timeout_s
        while True:
            if item.error is not None:
                raise item.error
            if item.result is not None:
                return item.result
            if time.monotonic() > deadline:
                raise QueueTimeoutError(
                    f"Queue wait timeout after {timeout_ms}ms for request {item.request_id}"
                )
            await asyncio.sleep(0.05)  # 50ms poll interval

    async def get_depth(self) -> int:
        """Return current queue depth."""
        async with self._lock:
            return len(self._queue)
