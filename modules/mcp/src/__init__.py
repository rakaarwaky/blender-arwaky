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
from .surface_execute_command import ExecuteCommandHandler
from .surface_get_config import GetConfigHandler
from .surface_health_check import HealthCheckHandler
from .surface_list_commands import ListCommandsHandler
from .surface_prompt_register import PromptHandlerModule
from .surface_read_skill import SkillDocumentationReader, SkillReadHandler
from .surface_server_instance import ServerInstanceHandler
from .surface_server_start import ServerStartHandler
from .surface_tool_registry import ToolRegistryHandler

__all__ = [
    "ExecuteCommandHandler",
    "GetConfigHandler",
    "HealthCheckHandler",
    "ListCommandsHandler",
    "PromptHandlerModule",
    "ServerInstanceHandler",
    "ServerStartHandler",
    "SkillDocumentationReader",
    "SkillReadHandler",
    "ToolRegistryHandler",
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
