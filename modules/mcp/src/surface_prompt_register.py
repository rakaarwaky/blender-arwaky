"""MCP Prompt registration for BlenderArwaky.

FR-MCP-001: Expose MCP Tools — PromptRegistrationModule registers prompt templates with FastMCP
FR-MCP-002: Route Tool Calls — prompts are routed through MCP server instance lifecycle
FR-MCP-003: Format MCP Responses — prompt responses follow standardized MCP format
"""

from mcp.server.fastmcp import FastMCP


class PromptRegistrationModule:
    """Module for MCP prompt registration."""

    @staticmethod
    def asset_creation_strategy() -> list[dict[str, object]]:
        """Defines the preferred strategy for creating assets in Blender."""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": (
                        "Create a Blender asset using the best available strategy.\n"
                        "When creating 3D content in Blender, always start by checking if integrations are available:\n"
                        "\n"
                        "0. Before anything, always check the tool_scene_ops from get_scene_info()\n"
                        "1. First use the following tools to verify if the following integrations are enabled:\n"
                        "    1. Poly Haven\n"
                        "        Use get_polyhaven_status() to verify its status ...\n"
                        "Only fall back to scripting when:\n"
                        "- Poly Haven and Sketchfab are both disabled\n"
                        "- A simple primitive is explicitly requested\n"
                        "- No suitable asset exists in any of the libraries\n"
                        "- The task specifically requires a basic material/color\n"
                    ),
                },
            }
        ]

    @staticmethod
    def lighting_expert() -> list[dict[str, object]]:
        from modules.mcp.src.prompts import get_lighting_expert_prompt

        return [{"role": "user", "content": {"type": "text", "text": get_lighting_expert_prompt()}}]

    @staticmethod
    def layout_expert() -> list[dict[str, object]]:
        from modules.mcp.src.prompts import get_layout_expert_prompt

        return [{"role": "user", "content": {"type": "text", "text": get_layout_expert_prompt()}}]

    @staticmethod
    def text_to_scene_orchestrator() -> list[dict[str, object]]:
        from modules.mcp.src.prompts import get_text_to_scene_orchestrator_prompt

        return [{"role": "user", "content": {"type": "text", "text": get_text_to_scene_orchestrator_prompt()}}]

    @staticmethod
    def register_prompts(mcp: FastMCP) -> None:
        """Register all prompt templates with the MCP server."""
        mcp.prompt(name="asset_creation_strategy")(PromptRegistrationModule.asset_creation_strategy)
        mcp.prompt(name="lighting_expert")(PromptRegistrationModule.lighting_expert)
        mcp.prompt(name="layout_expert")(PromptRegistrationModule.layout_expert)
        mcp.prompt(name="text_to_scene_orchestrator")(PromptRegistrationModule.text_to_scene_orchestrator)