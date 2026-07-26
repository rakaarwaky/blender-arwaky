"""Contract: Aggregate facade for the server feature.

Implemented by Agent layer to provide a unified interface
for connection lifecycle, code execution, command dispatch, and
async task management to the Surface layer.
AES Aggregate layer — depends only on Taxonomy and Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_server_vo import (
    ConnectionConfig,
    ConnectionStatus,
    ExecutionResult,
)


class IBlenderServerAggregate(ABC):
    """Aggregate facade for the server feature.

    Combines connection management, code execution, command dispatch,
    and async task management into a single unified interface consumed
    by the Surface layer.
    """

    # ─── Connection Lifecycle ──────────────────────────────

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Success: Returns ConnectionStatus with state='connected'
        Failure: Raises ConnectionConfigError, AuthenticationError, etc.
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent — no error if already closed."""
        ...

    @abstractmethod
    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        ...

    # ─── Code Execution ────────────────────────────────────

    @abstractmethod
    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Success: Returns ExecutionResult with status='success'
        Failure: Raises CodeValidationError, ExecutionTimeoutError, etc.
        """
        ...

    @abstractmethod
    async def submit_async_task(self, code: str, request_id: str) -> str:
        """Submit long-running code for async execution. Returns task_id."""
        ...

    @abstractmethod
    async def poll_task_result(self, task_id: str) -> ExecutionResult:
        """Poll async task status and final result.

        Failure: Raises TaskNotFoundError if not found or expired
        """
        ...

    # ─── Command Dispatch ──────────────────────────────────

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
    ) -> dict:  # noqa: ANN004
        """Dispatch a named command to Blender addon.

        Failure: Raises CommandTimeoutError if response exceeds configured timeout
        """
        ...
