"""MCP value objects — tool definitions, server config, response envelope.

NOTE: These VOs are defined per FRD schema but not currently consumed by any
contract protocol or capability. Kept as placeholder for future MCP contract
protocols (FR-MCP-001+). Remove if/when they become orphaned permanently.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class McpToolDef:
    """MCP tool definition for schema exposure.

    NOTE: Currently unused — kept as placeholder for future schema requirements.
    """

    name: str
    description: str
    parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class McpServerConfig:
    """MCP server configuration defaults.

    NOTE: Currently unused — kept as placeholder for future config requirements.
    """

    name: str = "blender-arwaky"
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass(frozen=True)
class McpResponse:
    """MCP response envelope structure.

    NOTE: Currently unused — kept as placeholder for future response requirements.
    Actual MCP responses use McpResponseImpl in mcp_response_formatter.py.
    """

    success: bool
    data: Any = None
    error: str | None = None
    tool: str | None = None
