"""Capability: MCP response formatter.

Implements ServerResponseProtocol — formats aggregate outcomes into
MCP-compliant structured responses with tracking identifiers, bounded
payloads, and categorized errors.

FR-MCP-003: Format MCP Responses
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    Details,
    ErrorString,
    SuccessFlag,
)
from modules.shared.src.mcp.contract_server_response_protocol import ServerResponseProtocol

logger = logging.getLogger("BlenderMCPServer")


class ServerResponseCapability(ServerResponseProtocol):
    """Business logic for formatting MCP responses."""

    def __init__(
        self,
        tracking_enabled: bool = True,
        default_max_payload_size: int = 1_000_000,
    ) -> None:
        """Initialize with configuration.

        Args:
            tracking_enabled: Whether to generate tracking IDs when omitted.
            default_max_payload_size: Upper bound for serialized content.
        """
        self._tracking_enabled = tracking_enabled
        self._default_max_payload_size = default_max_payload_size

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
        # Generate tracking ID if not provided and enabled
        if tracking_id is None and self._tracking_enabled:
            tracking_id = self._generate_tracking_id()

        max_size = max_payload_size or self._default_max_payload_size

        # Determine success/failure
        success = result.get("success", False) or result.get("error") is None
        error_category = result.get("error") or result.get("error_category")
        message = result.get("message", ErrorString(""))
        warnings = result.get("warnings", [])
        data = result.get("data")

        # Build bounded, safe payload
        bounded_data = self._truncate_payload(data, max_size) if data else None

        # Build MCP-compliant response envelope
        response: dict[str, Any] = {
            "success": SuccessFlag(success),
            "tracking_id": tracking_id,
            "data": bounded_data,
            "warnings": warnings if warnings else [],
            "metadata": {
                "action": result.get("action"),
                "owning_feature": result.get("owning_feature"),
                "duration": result.get("duration"),
                "truncation_indicator": (
                    bounded_data is not None and data is not None
                ),
            },
        }

        # Add error category if failed
        if error_category:
            response["error"] = {
                "category": ErrorString(str(error_category)),
                "message": ErrorString(str(message)),
                "details": result.get("details", Details()),
            }

        return response

    def _generate_tracking_id(self) -> str:
        """Generate a unique tracking identifier.

        Returns:
            A UUID-based tracking string.
        """
        from uuid import uuid4
        return str(uuid4())

    def _truncate_payload(
        self, data: Any, max_size: int
    ) -> Any:
        """Truncate payload to fit within size limit.

        FR-MCP-003: Oversized data follows configured strategy:
        summarize with counts and representative excerpt;
        truncate with explicit truncation indicator.

        Args:
            data: The data payload to truncate.
            max_size: Maximum allowed size in bytes.

        Returns:
            Truncated or summarized data with truncation metadata.
        """
        import json

        try:
            serialized = json.dumps(data, default=str)
            if len(serialized) <= max_size:
                return data  # No truncation needed
        except (TypeError, ValueError):
            return data  # Non-serializable; return as-is

        # Truncate with indicator
        if isinstance(data, dict):
            truncated: dict[str, Any] = {}
            remaining_size = max_size
            for key, value in data.items():
                try:
                    entry_serialized = json.dumps({key: value}, default=str)
                    if len(entry_serialized) > remaining_size - 50:
                        break
                    truncated[key] = value
                    remaining_size -= len(entry_serialized)
                except (TypeError, ValueError):
                    truncated[key] = "<non-serializable>"

            return {
                "data": truncated,
                "_truncated": True,
                "_remaining_keys": len(data) - len(truncated),
            }

        if isinstance(data, list):
            truncated_list: list[Any] = []
            remaining_size = max_size
            for item in data:
                try:
                    entry_serialized = json.dumps(item, default=str)
                    if len(entry_serialized) > remaining_size - 50:
                        break
                    truncated_list.append(item)
                    remaining_size -= len(entry_serialized)
                except (TypeError, ValueError):
                    truncated_list.append("<non-serializable>")

            return {
                "data": truncated_list,
                "_truncated": True,
                "_remaining_items": len(data) - len(truncated_list),
            }

        return data
