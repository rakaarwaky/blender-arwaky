"""MCP Tool 4: get_config — Retrieve BlenderArwaky configuration settings.

FR-MCP-001: Expose MCP Tools — register_get_config registers tool with MCP
FR-MCP-002: Route Tool Calls — config aggregate provides settings
FR-MCP-003: Format MCP Responses — config values returned as structured response
"""

from typing import Any


class GetConfigHandler:
    """Handler for the get_config MCP tool."""

    @staticmethod
    def register_get_config(mcp):
        """Register the get_config tool (MCP Tool #4)."""

        @mcp.tool()
        def get_config(
            key: str | None = None,
        ) -> Any:
            """
            Retrieve BlenderArwaky configuration settings.

            Args:
                key: Specific config key to retrieve. Omit for all settings.

            Returns:
                Config value(s) as structured response
            """
            from modules.config.src.root_config_container import get_config_snapshot

            snapshot = get_config_snapshot()
            if key:
                return snapshot.get(key, {"error": f"Unknown config key: {key}"})
            return snapshot
