"""MCP events — server lifecycle and tool invocation events.

NOTE: This file is defined per FRD event schema but currently unused by any
capability, agent, or surface layer. Kept as placeholder for future MCP event
requirements (FR-MCP-003+). Remove if/when events become orphaned permanently.
"""

from dataclasses import dataclass, field
from enum import StrEnum, auto

from ..common.taxonomy_core_vo import Details


class McpEventKind(StrEnum):
    """MCP event type enumeration."""

    SERVER_STARTED = auto()
    SERVER_STOPPED = auto()
    TOOL_INVOKED = auto()
    TOOL_SUCCEEDED = auto()
    TOOL_FAILED = auto()
    CONNECTION_OPENED = auto()
    CONNECTION_CLOSED = auto()


@dataclass(frozen=True)
class McpEvent:
    """MCP domain event for server lifecycle and tool invocations.

    NOTE: Currently unused — kept as placeholder for future event requirements.
    """

    kind: McpEventKind
    tool: str | None = None
    detail: str | None = None
    extra: Details = field(default_factory=dict)
