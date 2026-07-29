"""MCP value objects — tool definitions, server config, response envelope."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class McpToolDef:
    name: str
    description: str
    parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class McpServerConfig:
    name: str = "blender-arwaky"
    host: str = "127.0.0.1"
    port: int = 8080


@dataclass(frozen=True)
class McpResponse:
    success: bool
    data: Any = None
    error: str | None = None
    tool: str | None = None
