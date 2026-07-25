"""Contract: Aggregate facade for the server feature.

Implemented by Agent layer to provide a unified interface
for connection lifecycle, code execution, command dispatch, and
async task management to the Surface layer.
AES Aggregate layer — depends only on Taxonomy and Protocol.
"""

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_server_vo import ConnectionConfig, ConnectionStatus, ExecutionResult


class IBlenderServerAggregate(ABC):
    """Aggregate facade for the server feature.

    Combines connection management, code execution, command dispatch,
    and async task management into a single unified interface consumed
    by the Surface layer.
    """

    # ─── Connection Lifecycle ───────────────────────────────────

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent — no error if already closed."""
        pass

    @abstractmethod
    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        pass

    # ─── Code Execution ────────────────────────────────────────

    @abstractmethod
    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender."""
        pass

    @abstractmethod
    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution. Returns task_id and status."""
        pass

    @abstractmethod
    async def poll_task_result(self, task_id: str, request_id: str) -> ExecutionResult:
        """Poll async task status and final result."""
        pass

    # ─── Command Dispatch ──────────────────────────────────────

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:
        """Dispatch a named command to Blender addon.

        Routes through TCP socket with configurable timeout.
        Default timeout is 5000ms per FR-SRV-003.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            CommandTimeoutError: if response exceeds configured timeout.
        """
        pass
