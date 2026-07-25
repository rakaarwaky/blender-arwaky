"""Surface: MCP tool call mapping for Blender operations.

Smart surface that maps MCP tool inputs to Blender commands
via the IBlenderServerAggregate facade. Thin wrapper — no
business logic, no retry, no queueing, no timeout policy.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.server import (
    ConnectionConfig,
    IBlenderServerAggregate,
)
from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage

logger = logging.getLogger("BlenderMCPServer")


class BlenderSocketCommandSurface:
    """Smart surface for Blender socket operations.

    Maps MCP tool calls to Blender operations via the
    IBlenderServerAggregate facade. Strictly no business logic.
    """

    def __init__(self, aggregate: IBlenderServerAggregate) -> None:
        self._aggregate = aggregate

    async def connect(self, config: dict[str, Any]) -> dict[str, Any]:
        """Handle MCP connect tool call."""
        conn_config = ConnectionConfig(
            transport_type=config.get("transport_type", "socket"),
            host=config.get("host", "localhost"),
            port=config.get("port", 9876),
        )
        status = await self._aggregate.connect(conn_config)
        return {
            "status": "success",
            "data": {
                "state": status.state,
                "host": status.host,
                "port": status.port,
            },
        }

    async def disconnect(self) -> dict[str, Any]:
        """Handle MCP disconnect tool call."""
        await self._aggregate.disconnect()
        return {"status": "success", "data": None}

    async def get_status(self) -> dict[str, Any]:
        """Handle MCP get_connection_status tool call."""
        status = await self._aggregate.get_status()
        return {
            "status": "success",
            "data": {
                "state": status.state,
                "transport_type": status.transport_type,
                "host": status.host,
                "port": status.port,
                "protocol_version": status.protocol_version,
            },
        }

    async def execute_code(self, code: str, request_id: str = "") -> dict[str, Any]:
        """Handle MCP execute_blender_code tool call."""
        result = await self._aggregate.execute_code(code, request_id)
        return {
            "status": result.status,
            "data": result.data,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
            "truncated": result.truncated,
        }

    async def submit_async_task(self, code: str, request_id: str = "") -> dict[str, Any]:
        """Handle MCP submit_async_task tool call."""
        result = await self._aggregate.submit_async_task(code, request_id)
        return {"status": "success", "data": result}

    async def poll_task(self, task_id: str, request_id: str = "") -> dict[str, Any]:
        """Handle MCP poll_task_result tool call."""
        result = await self._aggregate.poll_task_result(task_id, request_id)
        return {
            "status": result.status,
            "data": result.data,
            "error": result.error,
        }

    async def send_command(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Handle MCP send_command tool call.

        Maps MCP tool input to Blender command dispatch.
        """
        try:
            result = await self._aggregate.execute_code(
                f"bpy.data.objects['{action}']",  # placeholder — real impl delegates properly
                request_id="",
            )
            return {"status": result.status, "data": result.data}
        except Exception as e:
            logger.error("Command dispatch failed: %s", e)
            return {
                "status": "error",
                "error": {"type": type(e).__name__, "message": str(e)},
            }
