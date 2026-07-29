"""MCP taxonomy — VOs, constants, contracts, and implementations for MCP surface type safety."""

from . import (
    contract_mcp_protocol,
    utility_response_formatter,
    utility_routing_proxy,
)
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

# Contract protocols (inbound behavior interfaces — Capabilities implement these)
from .contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
    McpSchemaProtocol,
)

# Utility functions (pure, stateless)
from .utility_response_formatter import envelope_with_tracking, mask_secrets, truncate_oversized
from .utility_routing_proxy import normalize_payload, route_tool_call, validate_execute_command_input

__all__ = [
    "DEFAULT_SERVER_NAME",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "TOOL_EXECUTE_COMMAND",
    "TOOL_HEALTH_CHECK",
    "TOOL_LIST_COMMANDS",
    "TOOL_READ_SKILL",
    "McpEventKind",
    "McpEvent",
    "McpToolDef",
    "McpServerConfig",
    "McpResponse",
    # Contracts
    "McpSchemaProtocol",
    "McpRoutingProtocol",
    "McpResponseProtocol",
    # Response utilities
    "envelope_with_tracking",
    "truncate_oversized",
    "mask_secrets",
    # Routing utilities
    "normalize_payload",
    "route_tool_call",
    "validate_execute_command_input",
]
