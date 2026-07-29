"""MCP Prompt registration for BlenderArwaky.

FR-MCP-001: Expose MCP Tools — PromptHandlerModule registers prompt templates with FastMCP
FR-MCP-002: Route Tool Calls — prompts are routed through MCP server instance lifecycle
FR-MCP-003: Format MCP Responses — prompt responses follow standardized MCP format
"""

from mcp.server.fastmcp import FastMCP


class PromptHandlerModule:
    """Handler for MCP prompt registration."""

    @staticmethod
    def asset_creation_strategy():
        """Defines the preferred strategy for creating assets in Blender"""
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": """Create a Blender asset using the best available strategy.
When creating 3D content in Blender, always start by checking if integrations are available:

0. Before anything, always check the tool_scene_ops from get_scene_info()
1. First use the following tools to verify if the following integrations are enabled:
    1. Poly Haven
        Use get_polyhaven_status() to verify its status ...
Only fall back to scripting when:
- Poly Haven and Sketchfab are both disabled
- A simple primitive is explicitly requested
- No suitable asset exists in any of the libraries
- The task specifically requires a basic material/color
""",
                },
            }
        ]

    @staticmethod
    def lighting_expert():
        from modules.mcp.src.prompts import get_lighting_expert_prompt

        return [{"role": "user", "content": {"type": "text", "text": get_lighting_expert_prompt()}}]

    @staticmethod
    def layout_expert():
        from modules.mcp.src.prompts import get_layout_expert_prompt

        return [{"role": "user", "content": {"type": "text", "text": get_layout_expert_prompt()}}]

    @staticmethod
    def text_to_scene_orchestrator():
        from modules.mcp.src.prompts import get_text_to_scene_orchestrator_prompt

        return [{"role": "user", "content": {"type": "text", "text": get_text_to_scene_orchestrator_prompt()}}]

    @staticmethod
    def register_prompts(mcp: FastMCP):
        mcp.prompt(name="asset_creation_strategy")(PromptHandlerModule.asset_creation_strategy)
        mcp.prompt(name="lighting_expert")(PromptHandlerModule.lighting_expert)
        mcp.prompt(name="layout_expert")(PromptHandlerModule.layout_expert)
        mcp.prompt(name="text_to_scene_orchestrator")(PromptHandlerModule.text_to_scene_orchestrator)


register_prompts = PromptHandlerModule.register_prompts


def get_layout_expert_prompt():
    from modules.mcp.src.prompts import get_layout_expert_prompt as _get

    return _get()


def get_text_to_scene_orchestrator_prompt():
    from modules.mcp.src.prompts import get_text_to_scene_orchestrator_prompt as _get

    return _get()
