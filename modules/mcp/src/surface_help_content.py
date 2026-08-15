"""MCP Tool 5: help — embedded usage documentation for MCP and CLI."""

from __future__ import annotations

from typing import Any

from modules.shared.src.mcp.taxonomy_mcp_constant import HELP_TOPICS
from modules.shared.src.mcp.utility_routing_proxy import build_help_result


def is_known_help_topic(topic: str | None) -> bool:
    """Return whether a help topic is present in the static taxonomy."""
    return str(topic or "overview").strip().lower() in HELP_TOPICS


class HelpSurface:
    """Register the embedded help tool as the fifth MCP core tool."""

    @staticmethod
    def register(mcp, container) -> None:
        """Register help without filesystem or SKILL.md dependencies."""

        async def help(topic: str | None = None) -> dict[str, Any]:
            """Explain how to use Blender Arwaky MCP and CLI tools.

            Args:
                topic: Optional topic: overview, mcp, cli, actions, safety, or examples.
            """
            result = build_help_result(topic)
            response = getattr(container, "response", None)
            if response is None:
                return result
            return await response.format_response(
                result=result,
                tool_name="help",
                tracking_id="",
                error_category=None if is_known_help_topic(topic) else "validation",
            )

        mcp.tool()(help)
