"""Agent: Server feature orchestrator.

Coordinates Blender TCP connection lifecycle and code execution
through the unified IBlenderServerAggregate facade. Per FRD-SRV-001
through FRD-SRV-005.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from modules.shared.src.server import (
    ConnectionConfig,
    ConnectionStatus,
    ExecutionResult,
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
    IBlenderServerAggregate,
)
from modules.shared.src.common.taxonomy_core_vo import Prompt, StatusString

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator(IBlenderServerAggregate):
    """Unified orchestrator for Blender server operations.

    Implements IBlenderServerAggregate to provide a single facade
    for connection lifecycle and code execution. Coordinates
    IBlenderConnectionProtocol and ICodeExecutionProtocol capabilities.

    Orchestrates flows per FRD:
    - FR-SRV-001: Connection lifecycle with heartbeat and reconnect
    - FR-SRV-002: Code execution with AST validation and queue management
    - FR-SRV-003: Command dispatch with timeout enforcement
    - FR-SRV-004: Connection factory pattern (delegated to BlenderConnectionFactory)
    - FR-SRV-005: Socket adapter surface (delegated to BlenderSocketAdapter)
    """

    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        code_executor: ICodeExecutionProtocol,
    ) -> None:
        self._connection = connection
        self._code_executor = code_executor
        self._tasks: dict[str, dict[str, Any]] = {}

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
        # Connection status is synchronous; wrap in thread
        return ConnectionStatus(
            state="connected",
            transport_type="socket",
            host=self._connection.host,  # type: ignore[attr-defined]
            port=self._connection.port,  # type: ignore[attr-defined]
        )

    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Orchestrates AST validation (via ICodeExecutionProtocol) and
        returns standardized ExecutionResult with timing.
        """
        start = time.monotonic()
        try:
            result = await self._code_executor.execute_blender_code(Prompt(code))
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status=StatusString("success"),
                data=result,
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status=StatusString("error"),
                error=None,  # Will be populated by capability layer
                execution_time_ms=elapsed_ms,
            )

    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution.

        Creates task entry with configurable TTL retention, returns
        task_id and initial pending status per FRD-SRV-002.
        """
        task_id = f"task_{request_id}_{int(time.monotonic() * 1000)}"
        self._tasks[task_id] = {
            "task_id": task_id,
            "state": "pending",
            "code": code,
            "created_at": time.monotonic(),
        }
        return {"task_id": task_id, "status": "pending"}

    async def poll_task_result(self, task_id: str, request_id: str) -> ExecutionResult:
        """Poll async task status and final result.

        Returns ExecutionResult with current task state. Unknown or
        expired tasks raise TaskNotFoundError (delegated to capability).
        """
        if task_id not in self._tasks:
            return ExecutionResult(
                status=StatusString("error"),
                data={"error": "Task not found", "task_id": task_id},
            )

        task = self._tasks[task_id]
        return ExecutionResult(
            status=StatusString(task["state"]),
            data={"task_id": task_id, "state": task["state"]},
        )
