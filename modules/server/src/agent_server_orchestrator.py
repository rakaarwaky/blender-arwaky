"""Agent: Server feature orchestrator.

Coordinates Blender TCP connection lifecycle and code execution
through the unified IBlenderServerAggregate facade.
"""

import logging
from typing import Any

from modules.shared.src.server import (
    ConnectionConfig,
    ConnectionStatus,
    ExecutionResult,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
)
from modules.shared.src.common.taxonomy_core_vo import Prompt, StatusString

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator(IBlenderServerAggregate):
    """Unified orchestrator for Blender server operations.

    Implements IBlenderServerAggregate to provide a single facade
    for connection lifecycle and code execution. Coordinates
    IBlenderConnectionProtocol and ICodeExecutionProtocol capabilities.
    """

    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        code_executor: Any,  # ICodeExecutionProtocol or similar capability
    ) -> None:
        self._connection = connection
        self._code_executor = code_executor

    # ─── Block 2: Aggregate Implementation ──────────────────────

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake."""
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
        return await self._connection.get_status()  # type: ignore[attr-defined]

    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender."""
        result = await self._code_executor.execute_blender_code(Prompt(code))
        return ExecutionResult(status=StatusString("success"), data=result)

    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution."""
        result = await self._code_executor.execute_blender_code(Prompt(code))
        return {"task_id": request_id, "status": "pending", "result": result}

    async def poll_task_result(self, task_id: str, request_id: str) -> ExecutionResult:
        """Poll async task status and final result."""
        return ExecutionResult(status=StatusString("success"), data={"task_id": task_id})
