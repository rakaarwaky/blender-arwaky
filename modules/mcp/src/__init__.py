"""MCP module public surface."""

from . import (
    surface_execute_command,
    surface_get_config,
    surface_health_check,
    surface_help,
    surface_list_commands,
    surface_prompt_register,
    surface_scene_tools,
    surface_server_instance,
    surface_server_start,
    surface_tool_registry,
)
from .surface_execute_command import ExecuteCommandSurface
from .surface_get_config import GetConfigSurface
from .surface_health_check import HealthCheckSurface
from .surface_help import HelpSurface
from .surface_list_commands import ListCommandsSurface
from .surface_prompt_register import PromptRegistrationModule
from .surface_server_instance import ServerInstanceSurface
from .surface_server_start import ServerStartSurface
from .surface_tool_registry import ToolRegistrySurface

__all__ = [
    "ExecuteCommandSurface",
    "GetConfigSurface",
    "HealthCheckSurface",
    "HelpSurface",
    "ListCommandsSurface",
    "PromptRegistrationModule",
    "ServerInstanceSurface",
    "ServerStartSurface",
    "ToolRegistrySurface",
    "surface_execute_command",
    "surface_get_config",
    "surface_health_check",
    "surface_help",
    "surface_list_commands",
    "surface_prompt_register",
    "surface_server_instance",
    "surface_server_start",
    "surface_tool_registry",
    "surface_scene_tools",
]
