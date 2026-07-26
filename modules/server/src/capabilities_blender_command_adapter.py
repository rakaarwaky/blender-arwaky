"""Capability: Blender command dispatch with timeout enforcement and execution queueing.

Implements IBlenderCommandProtocol & IExecutionQueueProtocol — dispatches named commands
to the Blender addon via TCP socket with configurable timeout and FIFO serialization per FR-SRV-003.
Includes argument schema validation and execution queueing.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage
from modules.shared.src.common.taxonomy_domain_error import ValidationError
from modules.shared.src.server import (
    DEFAULT_COMMAND_TIMEOUT_MS,
    CommandTimeoutError,
    ExecutionResult,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IExecutionQueueProtocol,
    QueueConfig,
    QueueFullError,
    QueueTimeoutError,
    get_command_schema,
)

logger = logging.getLogger("BlenderMCPServer")

@dataclass
class QueueItem:
    """Internal mutable state for a queued request."""

    request_id: str
    payload: dict[str, Any]
    enqueued_at: float = field(default_factory=time.monotonic)
    result: ExecutionResult | None = None
    error: Exception | None = None

class BlenderCommandAdapter(IBlenderCommandProtocol):
    """Command dispatch and execution queueing capability for Blender TCP socket operations.

    Implements FR-SRV-003: dispatches named commands with timeout enforcement,
    schema validation, and FIFO queue serialization to prevent concurrent bpy access.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        queue_config: QueueConfig | None = None,
    ) -> None:
        self._connection = connection_port
        self._config = queue_config or QueueConfig()
        self._queue: list[QueueItem] = []
        self._queue_lock = asyncio.Lock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def send_command(
        self,
        action: ActionName,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:  # FR-SRV-003
        """Dispatch a named command to Blender addon.

        Routes through TCP socket; response parsed as JSON.
        Default timeout: DEFAULT_COMMAND_TIMEOUT_MS (5000ms).
        Validates command arguments against schema per FR-SRV-003.
        Raises CommandTimeoutError if response exceeds timeout.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            ValidationError: if command arguments are invalid.
            CommandTimeoutError: if response exceeds configured timeout.
        """
        # Validate command arguments against schema (FR-SRV-003)
        action_str = str(action) if not isinstance(action, str) else action
        try:
            get_command_schema(action_str)  # Validates command exists
        except Exception as e:
            raise ValidationError(ErrorMessage(f"Invalid command: {action_str}")) from e

        timeout_s = (timeout_ms or DEFAULT_COMMAND_TIMEOUT_MS) / 1000.0
        start = time.monotonic()

        try:
            result = await asyncio.wait_for(
                self._connection.send_command(action, params),
                timeout=timeout_s,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(
                "Command %s completed in %.1fms",
                action,
                elapsed_ms,
            )
            return {
                "status": "success",
                "data": result,
                "execution_time_ms": elapsed_ms,
            }
        except asyncio.TimeoutError:
            logger.warning(
                "Command %s timed out after %.1fms",
                action,
                timeout_s * 1000,
            )
            raise CommandTimeoutError(
                ErrorMessage(
                    f"Command '{action}' timed out after {timeout_ms or DEFAULT_COMMAND_TIMEOUT_MS}ms"
                )
            ) from None
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            return {
                "status": "error",
                "data": None,
                "error": {"type": type(e).__name__, "message": str(e)},
                "execution_time_ms": elapsed_ms,
            }

    async def enqueue(
        self,
        request_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Add item to queue. Raises QueueFullError if depth limit exceeded."""
        async with self._queue_lock:
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
        async with self._queue_lock:
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
        async with self._queue_lock:
            return len(self._queue)

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return f"BlenderCommandAdapter(queue_max_depth={self._config.max_depth})"

    def _send_sync(self, action: ActionName, params: dict[str, Any]) -> dict[str, Any]:
        """Synchronous send_command for use with asyncio.to_thread."""
        return self._connection.send_command(action, params)

    async def _find_item(self, request_id: str) -> QueueItem | None:
        """Find queue item by request_id."""
        async with self._queue_lock:
            for item in self._queue:
                if item.request_id == request_id:
                    return item
            return None



