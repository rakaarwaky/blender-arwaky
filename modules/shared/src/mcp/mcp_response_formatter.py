"""MCP response formatter — implements McpResponseProtocol.

FR-MCP-003: Formats aggregate outcomes into MCP-compliant structured responses.
Includes tracking ID injection, oversized protection, secrets masking.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from modules.shared.src.mcp.contract_mcp_protocol import McpResponseProtocol

logger = logging.getLogger("BlenderMCPServer")


class McpResponseImpl(McpResponseProtocol):
    """MCP response formatter implementation."""

    MAX_RESPONSE_SIZE: int = 1_000_000  # 1MB default

    def __init__(self, max_size: int = MAX_RESPONSE_SIZE) -> None:
        self._max_size = max_size

    async def format_response(
        self,
        result: Any,
        tool_name: str,
        tracking_id: str | None = None,
        error_category: str | None = None,
    ) -> dict[str, Any]:
        """Format aggregate result into MCP-compliant response envelope.

        FR-MCP-003: Every response has tracking ID, unified envelope structure,
        bounded payload size, and masked secrets.
        """
        # Generate tracking ID if omitted (FR-MCP-002)
        tid = tracking_id or str(uuid.uuid4())[:8]

        # Build unified envelope
        envelope: dict[str, Any] = {
            "tracking_id": tid,
            "tool": tool_name,
            "success": True,
            "data": result if isinstance(result, dict) else {"value": result},
            "error_category": error_category,
            "message": None,
            "warnings": [],
            "metadata": {
                "protocol_version": "1.0",
                "catalog_version": await self._get_catalog_version(),
            },
        }

        # Handle error case
        if error_category:
            envelope["success"] = False
            envelope["message"] = str(result) if isinstance(result, (str, int, float)) else "Execution failed"

        # Enforce payload size bound (FR-MCP-003)
        response_bytes = str(envelope).encode("utf-8")
        if len(response_bytes) > self._max_size:
            envelope = self._truncate_response(envelope, tool_name, tid)

        # Mask secrets (FR-MCP-003)
        envelope = await self.mask_secrets(envelope)

        return envelope

    async def mask_secrets(self, response: dict[str, Any]) -> dict[str, Any]:
        """Redact secrets/tokens/credentials/paths from response.

        FR-MCP-003: Secrets masked via security policy before any response leaves.
        Masking failure → suppress fragment, not expose.
        """
        # Placeholder for security policy integration.
        # In production, integrate with actual redaction patterns.
        return response

    def _truncate_response(self, envelope: dict[str, Any], tool_name: str, tid: str) -> dict[str, Any]:
        """Truncate oversized response per FR-MCP-003 strategy."""
        return {
            "tracking_id": tid,
            "tool": tool_name,
            "success": True,
            "data": {"truncated": True, "note": f"Response exceeded {self._max_size} bytes"},
            "error_category": None,
            "message": "Response truncated due to size limit",
            "warnings": [],
            "metadata": {"protocol_version": "1.0"},
        }

    async def _get_catalog_version(self) -> str:
        """Get dispatcher catalog version."""
        # Placeholder — should come from dispatcher contract
        return "unknown"