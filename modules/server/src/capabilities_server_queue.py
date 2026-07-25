"""Capabilities: Execution queue for serialized Blender operations.

FIFO queue with depth limit and wait timeout that serializes requests
to prevent concurrent bpy access in Blender's single-threaded environment.
Implements IExecutionQueueProtocol.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.shared.src.server.contract_queue_protocol import IExecutionQueueProtocol
from modules.shared.src.server.taxonomy_server_error import QueueFullError, QueueTimeoutError
from modules.shared.src.server.taxonomy_server_vo import ExecutionResult, QueueConfig

logger = logging.getLogger("BlenderMCPServer")


@dataclass
class QueueItem:
    """Internal mutable state for a queued request."""

    request_id: str
    payload: dict[str, Any]
    enqueued_at: float = field(default_factory=time.monotonic)
    result: ExecutionResult | None = None
    error: Exception | None = None


class ExecutionQueue(IExecutionQueueProtocol):
    """FIFO execution queue with depth limit and wait timeout.

    Serializes requests to prevent concurrent bpy access.
    Rejects with QueueFullError when max_depth exceeded.
    Rejects with QueueTimeoutError when wait exceeds configured timeout.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, config: QueueConfig | None = None) -> None:
        self._config = config or QueueConfig()
        self._queue: list[QueueItem] = []
        self._lock = asyncio.Lock()

    # ─── Block 2: Protocol Method Implementation ─────────────
    async def enqueue(
        self,
        request_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Add item to queue. Raises QueueFullError if depth limit exceeded."""
        async with self._lock:
            if len(self._queue) >= self._config.max_depth:
                raise QueueFullError(
                    f"Queue full: {len(self._queue)}/{self._config.max_depth}"
                )

            item = QueueItem(request_id=request_id, payload=payload)
            self._queue.append(item)
            logger.info("Enqueued request %s (%d/%d)", request_id, len(self._queue), self._config.max_depth)
            return request_id

    async def dequeue(self) -> str | None:
        """Remove and return the next request_id from the queue."""
        async with self._lock:
            if not self._queue:
                return None
            item = self._queue.pop(0)
            logger.info("Dequeued request %s (%d remaining)", item.request_id, len(self._queue))
            return item.request_id

    async def wait_for_completion(
        self,
        request_id: str,
        timeout_ms: float | None = None,
    ) -> ExecutionResult:
        """Wait for a queued item to be processed and return result."""
        timeout_ms = timeout_ms or self._config.wait_timeout_ms
        timeout_s = timeout_ms / 1000.0

        item = await self._find_item(request_id)
        if item is None:
            raise QueueTimeoutError(f"Item not found: {request_id}")

        deadline = time.monotonic() + timeout_s
        while True:
            if item.error is not None:
                raise item.error
            if item.result is not None:
                return item.result
            if time.monotonic() > deadline:
                raise QueueTimeoutError(
                    f"Queue wait timeout after {timeout_ms}ms for request {request_id}"
                )
            await asyncio.sleep(0.05)

    async def get_depth(self) -> int:
        """Return current queue depth."""
        async with self._lock:
            return len(self._queue)

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return f"ExecutionQueue(max_depth={self._config.max_depth})"

    async def _find_item(self, request_id: str) -> QueueItem | None:
        """Find queue item by request_id."""
        async with self._lock:
            for item in self._queue:
                if item.request_id == request_id:
                    return item
            return None
