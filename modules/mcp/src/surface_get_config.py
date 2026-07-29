"""MCP Tool 4: get_config — Retrieve BlenderArwaky configuration settings.

FR-MCP-001: Expose MCP Tools — register via contract protocol
FR-MCP-002: Route Tool Calls — config aggregate via routing protocol
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


class GetConfigSurface:
    """Surface handler for get_config MCP tool.

    Delegates all logic to contract protocols — zero business logic.
    """

    def __init__(self, routing: McpRoutingProtocol, response: McpResponseProtocol) -> None:
        self._routing = routing
        self._response = response

    @staticmethod
    def register(mcp, container: McpContainer) -> None:
        """Register the get_config tool (MCP Tool #4)."""

        async def get_config(key: str | None = None) -> dict[str, Any]:
            """Retrieve BlenderArwaky configuration settings.

            Args:
                key: Specific config key to retrieve. Omit for all settings.

            Returns:
                Config value(s) as structured response
            """
            try:
                # Surface validates input; config retrieval routed via contract
                result = await container.routing.route_tool_call(
                    tool_name="get_config",
                    payload={"key": key},
                )
                return await container.response.format_response(
                    result=result,
                    tool_name="get_config",
                    tracking_id="",
                )
            except Exception as e:
                logger.error("get_config failed: %s", e, exc_info=True)
                return await container.response.format_response(
                    result={"error": str(e)},
                    tool_name="get_config",
                    tracking_id="",
                    error_category="execution",
                )

        mcp.tool()(get_config)