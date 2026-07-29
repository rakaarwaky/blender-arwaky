"""MCP events — server lifecycle and tool invocation events."""

from dataclasses import dataclass, field
from enum import StrEnum, auto


from . import taxonomy_mcp_constant as _taxonomy_mcp_constant  # AES202: mandatory taxonomy(constant) import


class McpEventKind(StrEnum):
    SERVER_STARTED = auto()
    SERVER_STOPPED = auto()
    TOOL_INVOKED = auto()
    TOOL_SUCCEEDED = auto()
    TOOL_FAILED = auto()
    CONNECTION_OPENED = auto()
    CONNECTION_CLOSED = auto()


@dataclass(frozen=True)
class McpEvent:
    kind: McpEventKind
    tool: str | None = None
    detail: str | None = None
    extra: dict[str, str] = field(default_factory=dict)
