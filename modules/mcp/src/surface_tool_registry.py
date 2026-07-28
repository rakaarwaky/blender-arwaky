"""MCP Tools Registry — Registers core MCP tools (AES handler layer).

FR-MCP-001: Expose MCP Tools — ToolRegistryHandler.register_tools() exposes execute_command/list_commands/read_skill_context/health_check
FR-MCP-002: Route Tool Calls — registry wires all tools to FastMCP router via tool decorators
FR-MCP-003: Format MCP Responses — all registered tools return standardized MCP response format

Tool list (unlimited CLI via single entry point):
  1. execute_command  — Universal action executor (dispatches to CLI)
  2. list_commands    — Command catalog discovery
  3. read_skill_context — SKILL.md documentation reader
  4. health_check     — System health diagnostics

All tools delegate to the agent layer; handlers never call capabilities directly.
"""


class ToolRegistryHandler:
    """Handler for tool registry ."""

    """Registry for all MCP tools. Handlers never call capabilities directly."""

    @staticmethod
    def register_tools(mcp):
        """
        Register the core MCP tools for BlenderArwaky.
        """
        from .surface_command_execute import CommandExecuteHandler
        from .surface_commands_list import CommandsListHandler
        from .surface_health_check import HealthCheckHandler
        from .surface_skill_read import SkillReadHandler

        # Tool 1: Universal executor
        CommandExecuteHandler.register_execute_command(mcp)

        # Tool 2: Command discovery
        CommandsListHandler.register_list_commands(mcp)

        # Tool 3: Documentation reader
        SkillReadHandler.register_read_skill_context(mcp)

        # Tool 4: Health check
        HealthCheckHandler.register_health_check(mcp)
