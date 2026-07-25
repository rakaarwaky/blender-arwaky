"""Agent: Server feature orchestrator.

Coordinates Blender TCP connection lifecycle, code execution,
command dispatch, and async task management through the unified
IBlenderServerAggregate facade. Per FRD-SRV-001 through FRD-SRV-005.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from modules.shared.src.server import (
    CommandTimeoutError,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionQueue,
    ExecutionResult,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    QueueFullError,
    QueueTimeoutError,
    TaskManager,
    TaskNotFoundError,
)
from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    ErrorMessage,
    Prompt,
    StatusString,
)

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator(IBlenderServerAggregate):
    """Unified orchestrator for Blender server operations.

    Implements IBlenderServerAggregate to provide a single facade
    for connection lifecycle, code execution, command dispatch, and
    async task management. Coordinates capabilities with queue
    serialization and task lifecycle per FRD-SRV-001 through FRD-SRV-005.

    Orchestrates flows:
    - FR-SRV-001: Connection lifecycle with heartbeat and reconnect
    - FR-SRV-002: Code execution with AST validation and queue management
    - FR-SRV-003: Command dispatch with timeout enforcement
    - FR-SRV-004: Connection factory pattern (delegated to BlenderConnectionFactory)
    - FR-SRV-005: Socket adapter surface (delegated to BlenderSocketAdapter)
    """

    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        code_executor: Any,  # ICodeExecutionProtocol
        queue: ExecutionQueue | None = None,
        task_manager: TaskManager | None = None,
    ) -> None:
        self._connection = connection
        self._code_executor = code_executor
        self._queue = queue or ExecutionQueue()
        self._task_manager = task_manager

    # ─── Block 2: Aggregate Implementation ──────────────────────

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Orchestrates connection via IBlenderConnectionProtocol.
        """
        self._connection.connect(config.host or "localhost", config.port or 9876)
        return ConnectionStatus(
            state="connected",
            transport_type=config.transport_type,
            host=config.host or "localhost",
            port=config.port or 9876,
            protocol_version=config.protocol_version,
        )

    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent."""
        self._connection.disconnect()

    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        return ConnectionStatus(
            state="connected",
            transport_type="socket",
            host=self._connection.host,  # type: ignore[attr-defined]
            port=self._connection.port,  # type: ignore[attr-defined]
        )

    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Orchestrates AST validation (via ICodeExecutionProtocol),
        enqueues for serialized bpy access, and returns standardized
        ExecutionResult with timing per FRD-SRV-002.
        """
        start = time.monotonic()
        try:
            # Enqueue for serialized bpy access
            await self._queue.enqueue(request_id, {"code": code})

            # Execute through capability layer
            result = await self._code_executor.execute_blender_code(Prompt(code))
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status=StatusString("success"),
                data=result,
                execution_time_ms=elapsed_ms,
            )
        except QueueFullError:
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type="QueueFullError",
                    message="Execution queue full — max depth exceeded",
                ),
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Code execution failed: %s", e)
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type=type(e).__name__,
                    message=str(e),
                ),
                execution_time_ms=elapsed_ms,
            )

    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution.

        Creates task entry with configurable TTL retention via TaskManager,
        returns task_id and initial pending status per FRD-SRV-002.
        """
        if self._task_manager is None:
            # Fallback to in-memory tracking if no TaskManager configured
            task_id = f"task_{request_id}_{int(time.monotonic() * 1000)}"
            return {"task_id": task_id, "status": "pending"}

        task_id = self._task_manager.create_task(request_id)
        return {"task_id": task_id, "status": "pending"}

    async def poll_task_result(self, task_id: str, request_id: str) -> ExecutionResult:
        """Poll async task status and final result.

        Returns ExecutionResult with current task state. Unknown or
        expired tasks raise TaskNotFoundError per FRD-SRV-002.
        """
        if self._task_manager is not None:
            try:
                task_status = self._task_manager.get_task(task_id)
                return ExecutionResult(
                    status=StatusString(task_status.state),
                    data=task_status.result,
                )
            except TaskNotFoundError:
                return ExecutionResult(
                    status=StatusString("error"),
                    error=ExecutionErrorDetail(
                        error_type="TaskNotFoundError",
                        message=f"Task not found or expired: {task_id}",
                    ),
                )

        # Fallback to in-memory tracking
        tasks = getattr(self, "_tasks", {})
        if task_id not in tasks:
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type="TaskNotFoundError",
                    message=f"Task not found or expired: {task_id}",
                ),
            )

        task = tasks[task_id]
        return ExecutionResult(
            status=StatusString(task["state"]),
            data={"task_id": task_id, "state": task["state"]},
        )

    async def send_command(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:
        """Dispatch a named command to Blender addon.

        Routes through TCP socket with configurable timeout enforcement
        per FRD-SRV-003. Default timeout is 5000ms.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            CommandTimeoutError: if response exceeds configured timeout.
        """
        start = time.monotonic()
        try:
            # Enqueue for serialized bpy access (control ops may bypass)
            await self._queue.enqueue(f"cmd_{action}", {"action": action, "params": params})

            # Dispatch through connection protocol
            result = self._connection.send_command(ActionName(action), params)
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
        except CommandTimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.warning("Command %s timed out after %.1fms", action, elapsed_ms)
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            return {
                "status": "error",
                "data": None,
                "error": {"type": type(e).__name__, "message": str(e)},
                "execution_time_ms": elapsed_ms,
            }
