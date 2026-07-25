"""
MCP Tools Registry — Registers core MCP tools (AES handler layer).

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
        from .surface_command_execute import register_execute_command
        from .surface_commands_list import register_list_commands
        from .surface_health_check import register_health_check
        from .surface_skill_read import register_read_skill_context

        # Tool 1: Universal executor
        register_execute_command(mcp)

        # Tool 2: Command discovery
        register_list_commands(mcp)

        # Tool 3: Documentation reader
        register_read_skill_context(mcp)

        # Tool 4: Health check
        register_health_check(mcp)


# Module-level alias for backward compatibility
register_tools = ToolRegistryHandler.register_tools
