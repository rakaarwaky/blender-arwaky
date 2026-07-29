"""MCP Tools Registry — Registers core MCP tools (AES handler layer).

FR-MCP-001: Expose MCP Tools — ToolRegistryHandler.register_tools() exposes 7 tools
FR-MCP-002: Route Tool Calls — registry wires all tools to FastMCP router via tool decorators
FR-MCP-003: Format MCP Responses — all registered tools return standardized MCP response format

Tool list:
  1. execute_command  — Universal action executor
  2. list_commands    — Command catalog discovery
  3. health_check     — System health diagnostics
  4. get_config       — Configuration retrieval
  5. read_skill_context — Static documentation reader
  6. inspect_scene    — Scene state inspection
  7. cleanup_scene    — Scene object cleanup
"""


class ToolRegistryHandler:
    """Registry for all MCP tools. Handlers delegate to contract protocols."""

    @staticmethod
    def register_tools(mcp):
        """Register all 5 MCP tools for BlenderArwaky."""
        from .surface_execute_command import ExecuteCommandHandler
        from .surface_get_config import GetConfigHandler
        from .surface_health_check import HealthCheckHandler
        from .surface_list_commands import ListCommandsHandler
        from .surface_read_skill import SkillReadHandler

        ExecuteCommandHandler.register_execute_command(mcp)
        ListCommandsHandler.register_list_commands(mcp)
        HealthCheckHandler.register_health_check(mcp)
        GetConfigHandler.register_get_config(mcp)
        SkillReadHandler.register_read_skill_context(mcp)

        # Scene tools require code_executor — registered separately when available
        from .surface_scene_tools import SceneToolsHandler
        SceneToolsHandler.register_scene_tools(mcp)
