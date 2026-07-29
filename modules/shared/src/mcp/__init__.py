"""MCP taxonomy — VOs, constants, contracts, and implementations for MCP surface type safety."""

from . import (
    contract_mcp_protocol,
    mcp_response_formatter,
    mcp_routing_proxy,
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

# Implementation classes
from .mcp_response_formatter import McpResponseImpl, McpSchemaImpl
from .mcp_routing_proxy import McpRoutingImpl

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
    # Contracts
    "McpSchemaProtocol",
    "McpRoutingProtocol",
    "McpResponseProtocol",
    # Implementations
    "McpSchemaImpl",
    "McpRoutingImpl",
    "McpResponseImpl",
]
