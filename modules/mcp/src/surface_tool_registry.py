"""MCP Tools Registry — Registers core MCP tools (AES handler layer).

FR-MCP-001: Expose MCP Tools — ToolRegistryHandler.register_tools() exposes 5 tools
FR-MCP-002: Route Tool Calls — registry wires all tools to FastMCP router via tool decorators
FR-MCP-003: Format MCP Responses — all registered tools return standardized MCP response format

Tool list:
  1. execute_command  — Universal action executor
  2. list_commands    — Command catalog discovery
  3. health_check     — System health diagnostics
  4. get_config       — Configuration retrieval
  5. read_skill_context — Static documentation reader
"""


class ToolRegistryHandler:
    """Registry for all MCP tools. Handlers never call capabilities directly."""

    @staticmethod
    def register_tools(mcp):
        """Register all 5 MCP tools for BlenderArwaky."""
        from .surface_execute_command import ExecuteCommandHandler
        from .surface_get_config import GetConfigHandler
        from .surface_health_check import HealthCheckHandler
        from .surface_list_commands import ListCommandsHandler
        from .surface_read_skill import SkillReadHandler

        # Tool 1: Universal executor
        ExecuteCommandHandler.register_execute_command(mcp)

        # Tool 2: Command discovery
        ListCommandsHandler.register_list_commands(mcp)

        # Tool 3: Health check
        HealthCheckHandler.register_health_check(mcp)

        # Tool 4: Config retrieval
        GetConfigHandler.register_get_config(mcp)

        # Tool 5: Documentation reader
        SkillReadHandler.register_read_skill_context(mcp)
