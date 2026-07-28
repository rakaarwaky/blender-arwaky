"""MCP surface — tool registration, server lifecycle, skill reading, and command routing."""

from . import surface_catalog_command
from . import surface_command_execute
from . import surface_commands_list
from . import surface_health_check
from . import surface_mcp_cli_wrapper
from . import surface_prompt_register
from . import surface_server_instance
from . import surface_server_start
from . import surface_skill_read
from . import surface_tool_registry
from .surface_catalog_command import CommandCatalogSurfaceHandler
from .surface_command_execute import CommandExecuteHandler
from .surface_commands_list import CommandsListHandler
from .surface_health_check import HealthCheckHandler
from .surface_prompt_register import PromptHandlerModule
from .surface_server_instance import ServerInstanceHandler
from .surface_server_start import ServerStartHandler
from .surface_skill_read import SkillDocumentationReader, SkillReadHandler
from .surface_tool_registry import ToolRegistryHandler

__all__ = [
    "CommandCatalogSurfaceHandler",
    "CommandExecuteHandler",
    "CommandsListHandler",
    "HealthCheckHandler",
    "PromptHandlerModule",
    "ServerInstanceHandler",
    "ServerStartHandler",
    "SkillDocumentationReader",
    "SkillReadHandler",
    "ToolRegistryHandler",
    "surface_catalog_command",
    "surface_command_execute",
    "surface_commands_list",
    "surface_health_check",
    "surface_mcp_cli_wrapper",
    "surface_prompt_register",
    "surface_server_instance",
    "surface_server_start",
    "surface_skill_read",
    "surface_tool_registry",
]
