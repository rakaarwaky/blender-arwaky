"""Agent: Server feature orchestrator.

Coordinates Blender TCP connection lifecycle, code execution,
command dispatch, and async task management through the unified
IBlenderServerAggregate facade. Per FRD-SRV-001 through FRD-SRV-005.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    Prompt,
    StatusString,
)
from modules.shared.src.server import (
    CommandTimeoutError,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    ICodeExecutionProtocol,
    QueueFullError,
    TaskNotFoundError,
)

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator(IBlenderServerAggregate):
    """Unified orchestrator for Blender server operations."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        code_executor: ICodeExecutionProtocol,
        command_adapter: IBlenderCommandProtocol | None = None,
    ) -> None:
        self._connection = connection
        self._code_executor = code_executor
        self._command_adapter = command_adapter

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Orchestrates connection via IBlenderConnectionProtocol.
        """
        await self._connection.connect()
        return ConnectionStatus(
            state="connected",
            transport_type=config.transport_type,
            host=config.host or "localhost",
            port=config.port or 9876,
            protocol_version=config.protocol_version,
        )

    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent."""
        await self._connection.disconnect()

    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        return await self._connection.get_status()

    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Orchestrates AST validation (via ICodeExecutionProtocol),
        enqueues for serialized bpy access, and returns standardized
        ExecutionResult with timing per FRD-SRV-002.
        """
        start = time.monotonic()
        try:
            # Enqueue for serialized bpy access
            if self._command_adapter is not None:
                await self._command_adapter.enqueue(request_id, {"code": code})

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
            logger.error("Code execution failed for request %s: %s", request_id, e)
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

        Delegates to ICodeExecutionProtocol capability layer per FRD-SRV-002.
        """
        logger.info("Submitting async task for request %s (code length=%d)", request_id, len(code))
        return await self._code_executor.submit_async_task(code, request_id)

    async def poll_task_result(self, task_id: str, request_id: str = "") -> ExecutionResult:
        """Poll async task status and final result.

        Delegates to ICodeExecutionProtocol capability layer per FRD-SRV-002.
        """
        logger.debug("Polling task %s for request %s", task_id, request_id)
        try:
            return await self._code_executor.poll_task_result(task_id, request_id)
        except TaskNotFoundError:
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type="TaskNotFoundError",
                    message=f"Task not found or expired: {task_id}",
                ),
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
            # Enqueue for serialized bpy access (non-scene read-only commands bypass queue per FR-003)
            is_non_scene = action.startswith("get_") or action in ("ping", "get_status", "get_version", "get_scene_info")
            if self._command_adapter is not None and not is_non_scene:
                await self._command_adapter.enqueue(f"cmd_{action}", {"action": action, "params": params})

            # Dispatch through connection protocol
            cmd_params = dict(params or {})
            if timeout_ms is not None:
                cmd_params["timeout_ms"] = timeout_ms

            result = await self._connection.send_command(ActionName(action), cmd_params)
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

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return "ServerOrchestrator()"
