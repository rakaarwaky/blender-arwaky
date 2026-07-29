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

logger = logging.getLogger("BlenderMCPServer")


class GetConfigHandler:
    """Surface handler for get_config MCP tool.

    Delegates all logic to contract protocols — zero business logic.
    """

    def __init__(self, routing: McpRoutingProtocol, response: McpResponseProtocol) -> None:
        self._routing = routing
        self._response = response

    @staticmethod
    def register_get_config(mcp):
        """Register the get_config tool (MCP Tool #4)."""
        from modules.mcp.src.root_mcp_container import create_mcp_feature

        container = create_mcp_feature()

        async def get_config(key: str | None = None) -> dict[str, Any]:
            """Retrieve BlenderArwaky configuration settings.

            Args:
                key: Specific config key to retrieve. Omit for all settings.

            Returns:
                Config value(s) as structured response
            """
            try:
                # Import config snapshot locally to avoid root container import
                from modules.config.src.root_config_container import get_config_snapshot

                snapshot = get_config_snapshot()
                if key:
                    result = snapshot.get(key, {"error": f"Unknown config key: {key}"})
                else:
                    result = snapshot
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
