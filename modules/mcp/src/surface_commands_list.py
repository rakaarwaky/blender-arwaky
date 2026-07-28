"""
MCP Tool 2: list_commands — Returns the command catalog (discovery).

FR-MCP-001: Expose MCP Tools — register_list_commands registers tool with MCP
FR-MCP-002: Route Tool Calls — get_container().core_agent_orchestrator.discover_actions routes to dispatcher
FR-MCP-003: Format MCP Responses — discovery outcome from the orchestrator

Lists all available actions, their parameters, descriptions, and domains.
FR-MCP-002 tool mapping: "List available actions" -> dispatcher feature, which
exposes catalog discovery via discover_actions (FR-DSP-002). The surface maps the
tool's ``domain`` filter onto the discovery capability_filter and the ``format``
onto discover_actions' detail_level.
Surface delegates to Agent container via its aggregate contract (AES compliant).
"""

from typing import Any

from modules.mcp.src.agent_mcp_orchestrator import get_container
from modules.shared.src.common.taxonomy_core_vo import DomainRef, FormatRef


class CommandsListHandler:
    """Handler for listing available MCP commands via agent container."""

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
            orchestrator = get_container().core_agent_orchestrator

            # Map the tool's format onto discover_actions' detail_level vocabulary
            # ('standard' = summary, 'full' = detailed). discover_actions raises on
            # any other value, so coerce explicitly.
            resolved_format = format or FormatRef("detailed")
            detail_level = "full" if str(resolved_format) == "detailed" else "standard"

            return orchestrator.discover_actions(
                name_filter=None,
                capability_filter=domain,
                detail_level=detail_level,
            )
