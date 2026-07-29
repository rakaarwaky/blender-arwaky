"""MCP Tool 3: health_check — Delegates to diagnostics aggregate for system health.

FR-MCP-001: Expose MCP Tools — register via contract protocol
FR-MCP-002: Route Tool Calls — diagnostics aggregate via routing protocol
FR-MCP-003: Format MCP Responses — unified envelope via response protocol
"""

import logging
from typing import Any

from modules.shared.src.mcp.contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class HealthCheckHandler:
    """Surface handler for health_check MCP tool.

    Delegates all logic to contract protocols — zero business logic.
    """

    def __init__(self, routing: McpRoutingProtocol, response: McpResponseProtocol) -> None:
        self._routing = routing
        self._response = response

    @staticmethod
    def register_health_check(mcp):
        """Register the health_check tool (MCP Tool #3)."""
        from modules.mcp.src.root_mcp_container import create_mcp_feature

        container = create_mcp_feature()

        async def health_check() -> dict[str, Any]:
            """Check the health and connectivity of BlenderArwaky."""
            try:
                result = await container.routing.route_tool_call(
                    tool_name="health_check",
                    payload={},
                )
                return await container.response.format_response(
                    result=result,
                    tool_name="health_check",
                    tracking_id="",
                )
            except Exception as e:
                logger.error("health_check failed: %s", e, exc_info=True)
                return await container.response.format_response(
                    result={"error": str(e)},
                    tool_name="health_check",
                    tracking_id="",
                    error_category="execution",
                )

        mcp.tool()(health_check)
