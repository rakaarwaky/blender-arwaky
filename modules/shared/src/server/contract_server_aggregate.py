"""Contract: Aggregate facade for the server feature.

Implemented by Agent layer to provide a unified interface
for connection lifecycle and code execution to the Surface layer.
AES Aggregate layer — depends only on Taxonomy and Protocol.
"""

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_server_vo import ConnectionConfig, ConnectionStatus, ExecutionResult


class IBlenderServerAggregate(ABC):
    """Aggregate facade for the server feature.

    Combines connection management and code execution into a single
    unified interface consumed by the Surface layer.
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
