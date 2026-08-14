"""Telemetry event type constants and allowlists.

FR-TLM-001: Allowlist of action types that may be recorded.
FR-TLM-002: Feature area taxonomy mapping.
"""

from __future__ import annotations

from typing import Final

EVENT_TYPE_STARTUP: Final[str] = "startup"
EVENT_TYPE_TOOL_EXECUTION: Final[str] = "tool_execution"
EVENT_TYPE_PROMPT_SENT: Final[str] = "prompt_sent"
EVENT_TYPE_CONNECTION: Final[str] = "connection"
EVENT_TYPE_ERROR: Final[str] = "error"

ALLOWED_ACTIONS: frozenset[str] = frozenset(
    [
        "action_execute",
        "action_list",
        "health_check",
        "settings_view",
        "task_status",
        "task_cancel",
        "search",
        "download",
        "import",
        "render",
        "screenshot",
    ]
)

FEATURE_AREAS: dict[str, str] = {
    "action_execute": "dispatcher",
    "action_list": "dispatcher",
    "health_check": "diagnostics",
    "settings_view": "config",
    "task_status": "job",
    "task_cancel": "job",
    "search": "asset",
    "download": "asset",
    "import": "asset",
    "render": "render",
    "screenshot": "render",
}
