"""MCP surface — 5 tools (execute_command, list_commands, health_check, get_config, read_skill_context) + per-domain action schemas."""

from . import (
    surface_execute_command,
    surface_get_config,
    surface_health_check,
    surface_list_commands,
    surface_prompt_register,
    surface_read_skill,
    surface_server_instance,
    surface_server_start,
    surface_tool_registry,
)
from .surface_execute_command import ExecuteCommandSurface
from .surface_get_config import GetConfigSurface
from .surface_health_check import HealthCheckSurface
from .surface_list_commands import ListCommandsSurface
from .surface_prompt_register import PromptRegistrationModule
from .surface_read_skill import SkillDocumentationReader, SkillReadSurface
from .surface_server_instance import ServerInstanceSurface
from .surface_server_start import ServerStartSurface
from .surface_tool_registry import ToolRegistrySurface

__all__ = [
    "ExecuteCommandSurface",
    "GetConfigSurface",
    "HealthCheckSurface",
    "ListCommandsSurface",
    "PromptRegistrationModule",
    "ServerInstanceSurface",
    "ServerStartSurface",
    "SkillDocumentationReader",
    "SkillReadSurface",
    "ToolRegistrySurface",
    "surface_execute_command",
    "surface_get_config",
    "surface_health_check",
    "surface_list_commands",
    "surface_prompt_register",
    "surface_read_skill",
    "surface_server_instance",
    "surface_server_start",
    "surface_tool_registry",
]
