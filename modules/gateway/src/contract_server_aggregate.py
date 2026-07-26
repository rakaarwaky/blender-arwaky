"""Contract: Aggregate facade for the server feature.

Implemented by Agent layer to provide a unified interface
for connection lifecycle, code execution, command dispatch, async tasks,
and metrics to the Surface layer.
AES Aggregate layer — depends only on Taxonomy and Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_server_vo import (
    CommandResult,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionResult,
    ServerMetrics,
    TaskStatus,
)


class IBlenderServerAggregate(ABC):
    """Aggregate facade for the server feature.

    Combines connection management, code execution, command dispatch,
    async task lifecycle, and metrics into a single unified interface
    consumed by the Surface layer.
    """

    # ─── Lifecycle ──────────────────────────────────────────────

    @abstractmethod
    async def start(self) -> None:
        """Initialize all server components. Must be called before use."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shut down all server components. Cancels pending operations."""
        ...

    # ─── Connection Lifecycle ──────────────────────────────────

    @abstractmethod
    async def connect(
        self,
        config: ConnectionConfig,
        request_id: str | None = None,
    ) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Success: Returns ConnectionStatus with state='connected'
        Failure: Raises ConnectionConfigError, AuthenticationError, etc.
        """
        ...

    @abstractmethod
    async def disconnect(
        self,
        request_id: str | None = None,
    ) -> None:
        """Graceful disconnect. Idempotent — no error if already closed."""
        ...

    @abstractmethod
    async def get_status(
        self,
        request_id: str | None = None,
    ) -> ConnectionStatus:
        """Return current connection state with metadata."""
        ...

    # ─── Code Execution ────────────────────────────────────────

    @abstractmethod
    async def execute_code(
        self,
        code: str,
        request_id: str | None = None,
    ) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Success: Returns ExecutionResult with status='success'
        Failure: Raises SecurityViolationError, ExecutionTimeoutError, etc.
        """
        ...

    # ─── Background Task Management ────────────────────────────

    @abstractmethod
    async def submit_async_task(
        self,
        code: str,
        request_id: str | None = None,
    ) -> str:
        """Submit long-running code for async execution. Returns task_id."""
        ...

    @abstractmethod
    async def poll_task_result(
        self,
        task_id: str,
        request_id: str | None = None,
    ) -> TaskStatus:
        """Poll async task status and final result.

        Failure: Raises TaskNotFoundError if not found or expired
        """
        ...

    @abstractmethod
    async def cancel_async_task(
        self,
        task_id: str,
        request_id: str | None = None,
    ) -> TaskStatus:
        """Cancel a pending or running background task."""
        ...

    # ─── Command Dispatch ──────────────────────────────────────

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: str | None = None,
    ) -> CommandResult:
        """Dispatch a named command to Blender addon.

        Failure: Raises CommandTimeoutError if response exceeds configured timeout
        """
        ...

    # ─── Metrics ───────────────────────────────────────────────

    @abstractmethod
    async def get_metrics(
        self,
        request_id: str | None = None,
    ) -> ServerMetrics:
        """Return current server metrics snapshot."""
        ...
