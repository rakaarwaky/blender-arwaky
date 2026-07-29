"""MCP domain contracts — tool routing, schema exposure, response formatting.

FR-MCP-001: Expose MCP Tools
FR-MCP-002: Route Tool Calls
FR-MCP-003: Format MCP Responses
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    Details,
    Prompt,
    ServerName,
)


class McpSchemaProtocol(ABC):
    """Protocol for exposing MCP tool schemas from dispatcher catalog."""

    @abstractmethod
    async def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool schema list with names, descriptions, params, examples.

        FR-MCP-001: Schemas assembled from owning features.
        Degraded tools listed with indicator, not hidden.
        """
        ...

    @abstractmethod
    async def get_catalog_version(self) -> str:
        """Return dispatcher catalog version for drift detection."""
        ...


class McpRoutingProtocol(ABC):
    """Protocol for routing tool calls to owning aggregates."""

    @abstractmethod
    async def route_tool_call(
        self,
        tool_name: str,
        payload: dict[str, Any],
        tracking_id: str | None = None,
    ) -> dict[str, Any]:
        """Route tool call to correct aggregate.

        FR-MCP-002: Every tool routes to same aggregate as CLI command.
        No retries, no reordering, no multi-aggregate composition.
        """
        ...

    @abstractmethod
    async def validate_tool_input(
        self,
        tool_name: str,
        payload: dict[str, Any],
        strict_mode: bool = True,
    ) -> list[str]:
        """Validate surface-level input shape.

        FR-MCP-002: Surface validates shape only (recognized, parsed, required fields).
        Semantic validation delegated to dispatcher + owning features.
        """
        ...


class McpResponseProtocol(ABC):
    """Protocol for formatting MCP-compliant responses."""

    @abstractmethod
    async def format_response(
        self,
        result: Any,
        tool_name: str,
        tracking_id: str,
        error_category: str | None = None,
    ) -> dict[str, Any]:
        """Format aggregate result into MCP-compliant response.

        FR-MCP-003: Structured per MCP spec with unified envelope.
        Tracking ID in every response. Payload size bounded.
        Secrets masked via security policy.
        """
        ...

    @abstractmethod
    async def mask_secrets(self, response: dict[str, Any]) -> dict[str, Any]:
        """Redact secrets/tokens/credentials/paths from response."""
        ...
