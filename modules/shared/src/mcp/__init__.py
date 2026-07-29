"""MCP taxonomy — VOs, constants, and events for MCP surface type safety."""

from .taxonomy_mcp_constant import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SERVER_NAME,
    TOOL_EXECUTE_COMMAND,
    TOOL_HEALTH_CHECK,
    TOOL_LIST_COMMANDS,
    TOOL_READ_SKILL,
)
from .taxonomy_mcp_event import McpEvent, McpEventKind
from .taxonomy_mcp_vo import McpResponse, McpServerConfig, McpToolDef

__all__ = [
    "DEFAULT_SERVER_NAME",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "TOOL_EXECUTE_COMMAND",
    "TOOL_LIST_COMMANDS",
    "TOOL_READ_SKILL",
    "TOOL_HEALTH_CHECK",
    "McpEventKind",
    "McpEvent",
    "McpToolDef",
    "McpServerConfig",
    "McpResponse",
]
