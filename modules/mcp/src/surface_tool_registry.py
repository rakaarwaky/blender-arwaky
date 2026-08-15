"""MCP core tool registry.

The public MCP surface intentionally exposes exactly five stable tools:
execute_command, list_commands, health_check, get_config, and help.
Feature actions remain available through execute_command and the CLI dispatcher.
"""


class ToolRegistrySurface:
    """Register the five stable MCP core tools."""

    @staticmethod
    def register_tools(mcp, container) -> None:
        """Register only the public core surface; no feature tool sprawl."""
        from .surface_execute_command import ExecuteCommandSurface
        from .surface_get_config import GetConfigSurface
        from .surface_health_check import HealthCheckSurface
        from .surface_help import HelpSurface
        from .surface_list_commands import ListCommandsSurface

        ExecuteCommandSurface.register(mcp, container)
        ListCommandsSurface.register(mcp, container)
        HealthCheckSurface.register(mcp, container)
        GetConfigSurface.register(mcp, container)
        HelpSurface.register(mcp, container)
