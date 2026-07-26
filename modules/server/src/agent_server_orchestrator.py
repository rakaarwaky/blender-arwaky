"""Agent: Server feature orchestrator.

Coordinates Blender connection lifecycle, code execution, command dispatch,
async task management, and operation queue processing through the unified
IBlenderServerAggregate facade per FRD-SRV-001 through FRD-SRV-005 (v2.0.0).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from modules.shared.src.server import (
    BlenderConnectionFailure,
    CommandResult,
    CommandTimeoutError,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    ICodeExecutionProtocol,
    IMetricsProvider,
    OperationWaitTimeoutError,
    ServerMetrics,
    TaskStatus,
    ValidationError,
    is_scene_mutating,
)

from modules.shared.src.server import (
    CONNECTION_STATE_CONNECTED,
    CONNECTION_STATE_DISCONNECTED,
    CONNECTION_STATE_FAILED,
    CONNECTION_STATE_RECONNECTING,
)

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator(IBlenderServerAggregate):
    """Unified orchestrator for Blender server operations.

    Implements IBlenderServerAggregate (v2.0.0). Owns the operation queue,
    serializes scene-mutating operations, bypasses non-scene commands,
    manages task lifecycle, and exposes metrics.
    """

    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        code_executor: ICodeExecutionProtocol,
        command_adapter: IBlenderCommandProtocol,
        operation_queue: "OperationQueue",  # type: ignore[name-defined]
        event_publisher: Any,  # IEventPublisher
        metrics_provider: IMetricsProvider,
        queue_wait_timeout_ms: float = 10_000.0,
        execution_default_timeout_ms: float = 30_000.0,
    ) -> None:
        """Initialize orchestrator with all dependencies.

        Args:
            connection: Blender connection protocol.
            code_executor: Code execution protocol.
            command_adapter: Command dispatch protocol.
            operation_queue: FIFO operation queue.
            event_publisher: Event bus for publishing events.
            metrics_provider: Metrics collector.
            queue_wait_timeout_ms: Default queue wait timeout.
            execution_default_timeout_ms: Default execution timeout.
        """
        self._connection = connection
        self._code_executor = code_executor
        self._command_adapter = command_adapter
        self._queue = operation_queue
        self._event_publisher = event_publisher
        self._metrics_provider = metrics_provider
        self._queue_wait_timeout_ms = queue_wait_timeout_ms
        self._execution_default_timeout_ms = execution_default_timeout_ms

        # Queue worker task
        self._queue_worker_task: asyncio.Task[None] | None = None
        self._running = False

    # ─── Block 2: Aggregate Implementation ────────────────────

    async def start(self) -> None:
        """Initialize all server components and start queue worker."""
        self._running = True
        self._queue_worker_task = asyncio.create_task(self._queue_worker_loop())
        logger.info("Server orchestrator started")

    async def shutdown(self) -> None:
        """Gracefully shut down all components. Cancels pending operations."""
        self._running = False

        # Cancel queue worker
        if self._queue_worker_task is not None:
            self._queue_worker_task.cancel()
            try:
                await self._queue_worker_task
            except asyncio.CancelledError:
                pass

        # Cancel all pending operations
        try:
            await self._queue.cancel_pending(ConnectionClosedError())
        except Exception as e:
            logger.warning("Error cancelling pending operations: %s", e)

        # Disconnect
        try:
            await self._connection.disconnect()
        except Exception as e:
            logger.warning("Error during disconnect: %s", e)

        logger.info("Server orchestrator shut down")

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Args:
            config: Connection configuration.

        Returns:
            ConnectionStatus with state='connected'.

        Raises:
            ConnectionConfigError, AuthenticationError, VersionMismatchError, etc.
        """
        status = await self._connection.connect(config)
        return status

    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent."""
        await self._connection.disconnect()

    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        return await self._connection.get_status()

    async def execute_code(self, code: str, request_id: str | None = None) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Enqueues for serialized bpy access (scene-mutating), waits for
        queue start and execution result, and returns standardized
        ExecutionResult with timing per FRD-SRV-002 (v2.0.0).

        Args:
            code: The Python code string to execute.
            request_id: Optional tracking ID.

        Returns:
            ExecutionResult with status, data, and timing.

        Raises:
            SecurityViolationError, ExecutionTimeoutError, etc.
        """
        # Check connection state — reject if not connected
        if self._connection._state not in (CONNECTION_STATE_CONNECTED,):  # type: ignore[attr-defined]
            raise BlenderConnectionFailure(
                message="Connection not established",
                details={"state": self._connection._state},  # type: ignore[attr-defined]
            )

        start = time.monotonic()

        try:
            # Enqueue for serialized execution
            from modules.shared.src.server import QueuedOperation, OPERATION_TYPE_CODE_SYNC
            operation = QueuedOperation(
                request_id=request_id or "",
                operation_type=OPERATION_TYPE_CODE_SYNC,
                payload={"code": code},
                timeout_ms=self._execution_default_timeout_ms,
                enqueued_at=time.monotonic(),
            )

            await self._queue.enqueue(operation)

            # Set active operation
            self._connection.set_active_operation_in_progress(True)  # type: ignore[attr-defined]

            try:
                # Wait for queue start
                await self._queue.wait_for_started(
                    operation.request_id,
                    timeout_ms=self._queue_wait_timeout_ms,
                )

                # Execute through capability layer
                result = await self._code_executor.execute_blender_code(code, request_id)

                # Mark complete
                await self._queue.complete(operation.request_id, result)

                elapsed_ms = (time.monotonic() - start) * 1000
                return ExecutionResult(
                    status="success",
                    data=result.data if hasattr(result, 'data') else result,
                    execution_time_ms=elapsed_ms,
                    truncated=getattr(result, 'truncated', False),
                    request_id=request_id,
                )

            finally:
                self._connection.set_active_operation_in_progress(False)  # type: ignore[attr-defined]

        except OperationWaitTimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status="error",
                error=ExecutionErrorDetail(
                    error_type="OperationWaitTimeoutError",
                    message="Operation waited too long to start",
                ),
                execution_time_ms=elapsed_ms,
                request_id=request_id,
            )
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Code execution failed for request %s: %s", request_id, e)
            return ExecutionResult(
                status="error",
                error=ExecutionErrorDetail(
                    error_type=type(e).__name__,
                    message=str(e),
                ),
                execution_time_ms=elapsed_ms,
                request_id=request_id,
            )

    async def submit_async_task(self, code: str, request_id: str | None = None) -> str:
        """Submit long-running code for async execution. Returns task_id."""
        logger.info("Submitting async task (code length=%d)", len(code))
        return self._code_executor.create_task(request_id)

    async def poll_task_result(self, task_id: str, request_id: str | None = None) -> TaskStatus:
        """Poll async task status and final result."""
        return await self._code_executor.poll_task_result(task_id, request_id)

    async def cancel_async_task(self, task_id: str, request_id: str | None = None) -> TaskStatus:
        """Cancel a pending or running background task."""
        return await self._code_executor.cancel_async_task(task_id, request_id)

    async def send_command(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
        request_id: str | None = None,
    ) -> CommandResult:
        """Dispatch a named command to Blender addon.

        Non-scene commands bypass the queue; scene-mutating commands are
        serialized through the FIFO queue per FR-SRV-003 (v2.0.0).

        Args:
            action: Named action to dispatch.
            params: Optional command arguments.
            timeout_ms: Override timeout in milliseconds.
            request_id: Optional tracking ID.

        Returns:
            CommandResult with status, data, and timing.

        Raises:
            ValidationError: If command is unknown or params are invalid.
            CommandTimeoutError: If response exceeds configured timeout.
        """
        # Check connection state
        if self._connection._state not in (CONNECTION_STATE_CONNECTED,):  # type: ignore[attr-defined]
            raise BlenderConnectionFailure(
                message="Connection not established",
                details={"state": self._connection._state},  # type: ignore[attr-defined]
            )

        start = time.monotonic()

        try:
            # Check if scene-mutating — serialize through queue
            if is_scene_mutating(action):
                from modules.shared.src.server import QueuedOperation, OPERATION_TYPE_COMMAND
                operation = QueuedOperation(
                    request_id=request_id or "",
                    operation_type=OPERATION_TYPE_COMMAND,
                    payload={"action": action, "params": params},
                    timeout_ms=timeout_ms or 5000.0,
                    enqueued_at=time.monotonic(),
                )

                await self._queue.enqueue(operation)

                try:
                    await self._queue.wait_for_started(
                        operation.request_id,
                        timeout_ms=self._queue_wait_timeout_ms,
                    )

                    result = await self._command_adapter.send_command(
                        action=action,
                        params=params,
                        timeout_ms=timeout_ms,
                        request_id=request_id,
                    )

                    await self._queue.complete(operation.request_id, result)
                    return result

                except OperationWaitTimeoutError:
                    elapsed_ms = (time.monotonic() - start) * 1000
                    logger.warning("Command %s wait timeout", action)
                    raise CommandTimeoutError(
                        action=action,
                        timeout_ms=self._queue_wait_timeout_ms,
                    ) from None

            else:
                # Non-scene command — bypass queue
                result = await self._command_adapter.send_command(
                    action=action,
                    params=params,
                    timeout_ms=timeout_ms,
                    request_id=request_id,
                )
                return result

        except ValidationError:
            raise
        except CommandTimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.warning("Command %s timed out after %.1fms", action, elapsed_ms)
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            return CommandResult(
                status="error",
                data=None,
                execution_time_ms=elapsed_ms,
                request_id=request_id,
            )

    async def get_metrics(self, request_id: str | None = None) -> ServerMetrics:
        """Return current server metrics snapshot."""
        return await self._metrics_provider.get_metrics(request_id)

    # ─── Block 3: Queue Worker Loop ────────────────────────────

    async def _queue_worker_loop(self) -> None:
        """FIFO queue worker — processes operations in submission order.

        Dequeues operations, sets active flag on connection, executes
        the appropriate handler (code or command), and marks complete/failed.
        """
        while self._running:
            try:
                operation = await self._queue.dequeue()
                if operation is None:
                    await asyncio.sleep(0.01)  # Brief yield
                    continue

                # Mark as started
                await self._queue.mark_started(operation.request_id)

                try:
                    if operation.operation_type == "code_sync":
                        code = operation.payload.get("code", "")
                        request_id = operation.request_id
                        result = await self._code_executor.execute_blender_code(code, request_id)
                        await self._queue.complete(operation.request_id, result)

                    elif operation.operation_type == "code_async":
                        # Background task — handled by code executor directly
                        await self._queue.complete(operation.request_id, "queued")

                    elif operation.operation_type == "command":
                        action = operation.payload.get("action", "")
                        params = operation.payload.get("params")
                        timeout = operation.timeout_ms
                        request_id = operation.request_id

                        result = await self._command_adapter.send_command(
                            action=action,
                            params=params,
                            timeout_ms=timeout,
                            request_id=request_id,
                        )
                        await self._queue.complete(operation.request_id, result)

                except asyncio.CancelledError:
                    await self._queue.fail(operation.request_id, asyncio.CancelledError())
                except Exception as e:
                    logger.error("Queue operation failed: %s", e)
                    await self._queue.fail(operation.request_id, e)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Queue worker error: %s", e)
                await asyncio.sleep(0.1)

    def __repr__(self) -> str:
        return "ServerOrchestrator()"
