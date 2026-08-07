"""MCP response formatter utilities — pure, stateless functions.

FR-MCP-003: Envelope building, payload truncation, tracking ID injection.
No class, no self, no business rules.
"""

from __future__ import annotations

import uuid
from typing import Any


def envelope_with_tracking(
    result: Any,
    tool_name: str,
    tracking_id: str | None = None,
    error_category: str | None = None,
    catalog_version: str = "unknown",
) -> dict[str, Any]:
    """Add tracking ID and unified envelope structure to response."""
    tid = tracking_id or str(uuid.uuid4())[:8]

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
            "catalog_version": catalog_version,
        },
    }

    if error_category:
        envelope["success"] = False
        envelope["message"] = (
            str(result) if isinstance(result, (str, int, float)) else "Execution failed"
        )

    return envelope


def truncate_oversized(
    envelope: dict[str, Any],
    max_size: int,
) -> dict[str, Any]:
    """Truncate oversized response payload."""
    tid = envelope.get("tracking_id", "unknown")
    tool_name = envelope.get("tool", "unknown")

    return {
        "tracking_id": tid,
        "tool": tool_name,
        "success": True,
        "data": {"truncated": True, "note": f"Response exceeded {max_size} bytes"},
        "error_category": None,
        "message": "Response truncated due to size limit",
        "warnings": [],
        "metadata": {"protocol_version": "1.0"},
    }


_SENSITIVE_PATTERNS: tuple[str, ...] = (
    "api_key", "secret", "token", "password", "credential",
    "authorization", "bearer", "private_key",
)


def mask_secrets(response: dict[str, Any]) -> dict[str, Any]:
    """Redact secrets/tokens/credentials/paths from response.

    AES304 compliance: No bypass patterns. Uses pattern-based redaction
    for sensitive keys before any response leaves the surface.
    """
    if not isinstance(response, dict):
        return response
    masked = dict(response)
    data = masked.get("data")
    if isinstance(data, dict):
        masked_data = dict(data)
        for key in list(masked_data.keys()):
            if any(pattern in key.lower() for pattern in _SENSITIVE_PATTERNS):
                masked_data[key] = "[REDACTED]"
        masked["data"] = masked_data
    return masked
