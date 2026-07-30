"""MCP value objects — tool definitions, server config, response envelope."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class McpToolDef:
    """MCP tool definition for schema exposure."""

    name: str
    description: str
    parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class McpServerConfig:
    """MCP server configuration defaults."""

    name: str = "blender-arwaky"
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass(frozen=True)
class McpServerBootstrapVO:
    """MCP server bootstrap configuration Value Object (Taxonomy layer)."""

    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8080
    log_file: str = ""

    def is_sse(self) -> bool:
        """Check if transport mode is SSE."""
        return self.transport == "sse"

    def to_host_port(self) -> tuple[str, int]:
        """Return (host, port) tuple."""
        return (self.host, self.port)


@dataclass(frozen=True)
class McpResponse:
    """MCP response envelope structure."""

    success: bool
    data: Any = None
    error: str | None = None
    tool: str | None = None
