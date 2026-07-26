"""MCP domain contract: server response protocol (ABC based).

Defines the protocol for formatting and serializing aggregate outcomes
into MCP-compliant structured responses with tracking identifiers,
bounded payloads, and categorized errors.

FR-MCP-003: Format MCP Responses
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ServerResponseProtocol(ABC):
    """Protocol for formatting aggregate outcomes into MCP-compliant responses."""

    @abstractmethod
    async def format_response(
        self,
        result: dict[str, Any],
        tracking_id: str | None = None,
        max_payload_size: int | None = None,
    ) -> dict[str, Any]:
        """Format aggregate outcome into MCP-compliant structured response.

        FR-MCP-003: Every response is structured per MCP specification.
        Tracking identifier appears in every response (success or failure).
        Payload size is bounded by configured maximum.
        Secrets are masked through security policy rules before transmission.

        Args:
            result: Aggregate result or error with tracking identifier.
            tracking_id: Optional tracking identifier; generated if omitted.
            max_payload_size: Optional upper bound for serialized content.

        Returns:
            MCP response dict with success, data, error category, message,
            tracking ID, warnings, and metadata.
        """
        pass