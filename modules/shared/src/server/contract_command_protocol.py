"""Contract: Command dispatch protocol for Blender operations.

Implemented by Capabilities layer (BlenderCommandAdapter).
Per FR-SRV-003: Send Blender Commands via TCP socket with timeout enforcement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ActionName


from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ActionName
from .taxonomy_server_vo import ExecutionResult


class IBlenderCommandProtocol(ABC):
    """Protocol for dispatching named commands and managing execution queueing.

    Implemented by Capabilities layer (BlenderCommandAdapter). Each command is routed through
    TCP socket with configurable timeout enforcement per FR-SRV-003, with FIFO queue serialization.
    """

    @abstractmethod
    async def send_command(
        self,
        action: ActionName,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:
        """Dispatch a named command to Blender addon.

        Routes through TCP socket; response parsed as JSON.
        Default timeout: 5000ms (DEFAULT_COMMAND_TIMEOUT_MS).
        Raises CommandTimeoutError if response exceeds timeout.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            CommandTimeoutError: if response exceeds configured timeout.
        """
        ...

    @abstractmethod
    async def enqueue(
        self,
        request_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Add item to queue. Raises QueueFullError if depth limit exceeded."""
        ...

    @abstractmethod
    async def dequeue(self) -> str | None:
        """Remove and return the next request_id from the queue."""
        ...

    @abstractmethod
    async def wait_for_completion(
        self,
        request_id: str,
        timeout_ms: float | None = None,
    ) -> ExecutionResult:
        """Wait for a queued item to be processed and return result."""
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        """Return current queue depth."""
        ...

