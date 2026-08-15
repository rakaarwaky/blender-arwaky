"""MCP response formatter — implements McpResponseProtocol.

FR-MCP-003: Formats aggregate outcomes into MCP-compliant structured responses.
Includes tracking ID injection, oversized protection, secrets masking.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import RequestId, ToolName
from modules.shared.src.mcp.contract_mcp_protocol import McpResponseProtocol

logger = logging.getLogger("BlenderMCPServer")


class McpResponseImpl(McpResponseProtocol):
    """MCP response formatter implementation."""

    MAX_RESPONSE_SIZE: int = 1_000_000  # 1MB default

    def __init__(
        self,
        max_size: int = MAX_RESPONSE_SIZE,
        catalog_version: str = "unknown",
        redaction_policy: Callable[[str], Awaitable[str]] | None = None,
    ) -> None:
        self._max_size = max_size
        self._catalog_version = catalog_version
        self._redaction_policy = redaction_policy

    async def format_response(
        self,
        result: Any,
        tool_name: ToolName,
        tracking_id: RequestId | None = None,
        error_category: str | None = None,
    ) -> dict[str, Any]:
        """Format aggregate result into MCP-compliant response envelope.

        FR-MCP-003: Every response has tracking ID, unified envelope structure,
        bounded payload size, and masked secrets.
        """
        # Preserve an upstream tracking ID when the caller leaves the argument empty.
        upstream_tracking_id = result.get("tracking_id") if isinstance(result, dict) else None
        tid = tracking_id or upstream_tracking_id or str(uuid.uuid4())[:8]

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
        """Recursively redact sensitive keys and values before transmission."""
        sensitive_keys = {
            "token",
            "secret",
            "password",
            "credential",
            "api_key",
            "authorization",
            "auth_token",
            "path",
            "file_path",
            "code",
            "prompt",
        }

        async def redact(value: Any, key: str | None = None) -> Any:
            if key and any(pattern in key.lower() for pattern in sensitive_keys):
                return "[REDACTED]"
            if isinstance(value, dict):
                return {
                    str(item_key): await redact(item_value, str(item_key)) for item_key, item_value in value.items()
                }
            if isinstance(value, list):
                return [await redact(item) for item in value]
            if isinstance(value, tuple):
                return [await redact(item) for item in value]
            if isinstance(value, str) and self._redaction_policy is not None:
                return await self._redaction_policy(value)
            return value

        result = await redact(response)
        return result if isinstance(result, dict) else {"data": result}

    def _truncate_response(self, _envelope: dict[str, Any], tool_name: ToolName, tid: RequestId) -> dict[str, Any]:
        """Truncate oversized response per FR-MCP-003 strategy."""
        return {
            "tracking_id": tid,
            "tool": tool_name,
            "success": True,
            "data": {"truncated": True, "note": f"Response exceeded {self._max_size} bytes"},
            "error_category": None,
            "message": "Response truncated due to size limit",
            "warnings": [],
            "metadata": {"protocol_version": "1.0", "catalog_version": self._catalog_version},
        }

    async def _get_catalog_version(self) -> str:
        """Return the deterministic dispatcher catalog version supplied at wiring."""
        return self._catalog_version
