"""MCP Tool 2: list_commands — Returns command catalog from dispatcher catalog + action schemas.

FR-MCP-001: Expose MCP Tools — register via contract protocol
FR-MCP-002: Route Tool Calls — dispatcher aggregate discover_actions via routing protocol
FR-MCP-003: Format MCP Responses — unified envelope via response protocol
"""

import logging
from typing import Any

from modules.shared.src.mcp.contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
)
from modules.mcp.src.root_mcp_container import McpContainer

logger = logging.getLogger("BlenderMCPServer")

#: Maximum allowed payload size for tool call arguments (bytes)
MAX_PAYLOAD_SIZE = 1_000_000  # 1MB


class ListCommandsSurface:
    """Surface handler for list_commands MCP tool.

    Delegates all logic to contract protocols — zero business logic.
    """

    def __init__(self, routing: McpRoutingProtocol, response: McpResponseProtocol) -> None:
        self._routing = routing
        self._response = response

    @staticmethod
    def register(mcp, container: McpContainer) -> None:
        """Register the list_commands tool (MCP Tool #2)."""

        async def list_commands(
            domain: str | None = None,
            format: str | None = None,
        ) -> dict[str, Any]:
            """List all available BlenderArwaky actions."""
            try:
                result = await container.routing.route_tool_call(
                    tool_name="list_commands",
                    payload={"domain": domain, "format": format},
                )
                return await container.response.format_response(
                    result=result,
                    tool_name="list_commands",
                    tracking_id="",
                )
            except Exception as e:
                logger.error("list_commands failed: %s", e, exc_info=True)
                return await container.response.format_response(
                    result={"error": str(e)},
                    tool_name="list_commands",
                    tracking_id="",
                    error_category="execution",
                )

        mcp.tool()(list_commands)