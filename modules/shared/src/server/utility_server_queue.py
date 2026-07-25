"""Utility: Serialized execution queue for bpy thread safety.

Stateless standalone functions and a thread-safe queue for serializing
Blender Python API calls. bpy is not thread-safe and must run on
Blender's main thread.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from ..common.taxonomy_core_vo import ErrorMessage
from ..server.taxonomy_server_error import QueueFullError, QueueTimeoutError

logger = logging.getLogger("BlenderMCPServer")


@dataclass(frozen=True)
class QueueConfig:
    """Configuration for the execution queue."""
    max_depth: int = 50
    wait_timeout_seconds: float = 10.0


@dataclass
class QueueEntry:
    """A single entry in the execution queue."""
    request_id: str
    coroutine_factory: Callable[[], Coroutine[Any, Any, Any]]
    future: asyncio.Future
    enqueued_at: float = field(default_factory=time.monotonic)


class ExecutionQueue:
    """Thread-safe FIFO queue for serializing Blender execution requests.

    All requests that access Blender state must go through this queue
    to prevent race conditions from bpy's single-threaded constraint.
    """

    def __init__(self, config: QueueConfig | None = None) -> None:
        self._config = config or QueueConfig()
        self._queue: deque[QueueEntry] = deque()
        self._processing = False
        self._lock = asyncio.Lock()

    @property
    def depth(self) -> int:
        """Current number of pending entries."""
        return len(self._queue)

    @property
    def is_full(self) -> bool:
        """Check if queue has reached max depth."""
        return self.depth >= self._config.max_depth

    async def enqueue(
        self,
        request_id: str,
        coroutine_factory: Callable[[], Coroutine[Any, Any, Any]],
        loop: asyncio.AbstractEventLoop,
    ) -> asyncio.Future:
        """Add a request to the queue. Raises QueueFullError if at capacity."""
        if self.is_full:
            raise QueueFullError(
                ErrorMessage(
                    f"Execution queue full: {self.depth}/{self._config.max_depth}"
                )
            )

        future = loop.create_future()
        entry = QueueEntry(
            request_id=request_id,
            coroutine_factory=coroutine_factory,
            future=future,
        )
        self._queue.append(entry)
        logger.info(
            "Enqueued request %s (depth=%d)", request_id, self.depth
        )

        # Start processing if not already running
        if not self._processing:
            asyncio.ensure_future(self._process_next())

        return future

    async def _process_next(self) -> None:
        """Process the next entry in the queue."""
        async with self._lock:
            if not self._queue:
                self._processing = False
                return

            self._processing = True
            entry = self._queue.popleft()

            # Check wait timeout
            wait_time = time.monotonic() - entry.enqueued_at
            if wait_time > self._config.wait_timeout_seconds:
                entry.future.set_exception(
                    QueueTimeoutError(
                        ErrorMessage(
                            f"Queue wait timeout: waited {wait_time:.1f}s "
                            f"(max: {self._config.wait_timeout_seconds}s)"
                        )
                    )
                )
                # Process next
                if self._queue:
                    asyncio.ensure_future(self._process_next())
                else:
                    self._processing = False
                return

            logger.info(
                "Processing request %s (waited %.1fs)",
                entry.request_id,
                wait_time,
            )

            try:
                result = await entry.coroutine_factory()
                if not entry.future.cancelled():
                    entry.future.set_result(result)
            except Exception as e:
                if not entry.future.cancelled():
                    entry.future.set_exception(e)

            # Process next entry
            if self._queue:
                asyncio.ensure_future(self._process_next())
            else:
                self._processing = False

    def clear(self) -> None:
        """Clear all pending entries. Fails them with QueueFullError."""
        while self._queue:
            entry = self._queue.popleft()
            if not entry.future.cancelled():
                entry.future.set_exception(
                    QueueFullError(ErrorMessage("Queue cleared"))
                )
        self._processing = False
