"""MCP domain contract: tool schema exposure protocol (ABC based).

AES Contract layer — pure ABC definition, no implementation.

FR-MCP-001: Expose MCP Tools
- Publishes the system's capabilities as MCP-compliant tool schemas
- The dispatcher action catalog is the single source of action semantics
- This feature renders the catalog; it never redefines action meaning
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class McpToolExposureProtocol(ABC):
    """Protocol for rendering the dispatcher catalog as MCP tool schemas."""

    @abstractmethod
    def expose_tool_schemas(self) -> list[dict]:
        """Render every registered action as an MCP tool schema.

        FR-MCP-001: Tool name, AI-readable description, parameter schema, and
        usage examples all derive from the dispatcher catalog. Returns a list of
        MCP-compliant schema dicts (name, description, inputSchema, examples).
        """
        pass

    @abstractmethod
    def expose_tool(self, action_name: str) -> dict | None:
        """Render a single action as an MCP tool schema, or None if absent.

        FR-MCP-001: Lookups never redefine semantics — they project the catalog.
        """
        pass

    @abstractmethod
    def source_catalog_version(self) -> int:
        """Return the dispatcher catalog version this exposure was rendered from."""
        pass
