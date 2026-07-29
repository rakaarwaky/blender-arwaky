"""MCP routing proxy utilities — pure, stateless functions.

FR-MCP-002: Payload normalization and input validation.
No class, no self, no business rules.
"""

from __future__ import annotations

from typing import Any


def normalize_payload(payload: Any) -> dict[str, Any]:
    """Ensure payload is a dict; coerce non-dict to empty dict."""
    if isinstance(payload, dict):
        return payload
    return {}


def validate_execute_command_input(payload: dict[str, Any]) -> list[str]:
    """Validate surface-level input shape for execute_command tool.

    Checks that 'action' field is present and non-empty.
    Semantic validation is delegated to the dispatcher.
    """
    action = payload.get("action")
    if not action or not str(action).strip():
        return ["action is required"]
    return []
