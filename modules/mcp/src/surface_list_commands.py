"""MCP Tool 2: list_commands — Returns command catalog from dispatcher catalog + action schemas.

FR-MCP-001: Expose MCP Tools — register_list_commands registers tool with MCP
FR-MCP-002: Route Tool Calls — dispatcher aggregate discover_actions provides catalog
FR-MCP-003: Format MCP Responses — discovery outcome from orchestrator
"""

from typing import Any

from modules.dispatcher.src.root_dispatcher_container import create_dispatcher_feature
from modules.shared.src.common.taxonomy_core_vo import DomainRef, FormatRef


class ListCommandsHandler:
    """Handler for the list_commands MCP tool."""

    @staticmethod
    def register_list_commands(mcp):
        """Register the list_commands tool (MCP Tool #2)."""

        @mcp.tool()
        def list_commands(
            domain: DomainRef | None = None,
            format: FormatRef | None = None,
        ) -> Any:
            """
            List all available BlenderArwaky actions.

            Args:
                domain: Filter by domain (scene, object, viewport, render, io, infrastructure, asset, generation). Omit to list all.
                format: Output format — 'detailed' (full spec per action) or 'summary' (names + descriptions only)

            Returns:
                Discovery outcome with the command catalog
            """
            orchestrator = create_dispatcher_feature()
            resolved_format = format or FormatRef("detailed")
            detail_level = "full" if str(resolved_format) == "detailed" else "standard"

            return orchestrator.discover_actions(
                name_filter=None,
                capability_filter=domain,
                detail_level=detail_level,
            )
