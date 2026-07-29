"""MCP surface — 5 tools (execute_command, list_commands, health_check, get_config, read_skill_context) + per-domain action schemas."""

from . import surface_action_registry
from . import surface_asset_action
from . import surface_config_action
from . import surface_execute_command
from . import surface_get_config
from . import surface_health_check
from . import surface_job_action
from . import surface_launcher_action
from . import surface_list_commands
from . import surface_object_action
from . import surface_prompt_register
from . import surface_read_skill
from . import surface_render_action
from . import surface_scene_action
from . import surface_server_instance
from . import surface_server_start
from . import surface_tool_registry
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
    "surface_action_registry",
    "surface_asset_action",
    "surface_config_action",
    "surface_execute_command",
    "surface_get_config",
    "surface_health_check",
    "surface_job_action",
    "surface_launcher_action",
    "surface_list_commands",
    "surface_object_action",
    "surface_prompt_register",
    "surface_read_skill",
    "surface_render_action",
    "surface_scene_action",
    "surface_server_instance",
    "surface_server_start",
    "surface_tool_registry",
]
