"""Telemetry event taxonomy — PII-free event types and allowlists.

FRD hard rule: Never store customer_uuid, error messages, prompts, or
user-identifiable content in telemetry records.

FR-TLM-001: Allowlist of action types that may be recorded.
FR-TLM-002: Feature area taxonomy mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from modules.shared.src.common.taxonomy_core_vo import (
    PlatformName,
    SessionId,
    Timestamp,
    VersionString,
)


class TelemetryCategory(Enum):
    """Fixed low-cardinality telemetry categories (FR-TLM-002)."""

    STARTUP = "startup"
    TOOL_EXECUTION = "tool_execution"
    PROMPT_SENT = "prompt_sent"
    CONNECTION = "connection"
    ERROR = "error"
    OTHER = "other"


# Allowlist of action types that may be recorded (FR-TLM-001)
ALLOWED_ACTIONS: frozenset[str] = frozenset([
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
])

# Feature area taxonomy mapping (FR-TLM-002)
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


@dataclass(frozen=True)
class TelemetryEvent:
    """PII-free telemetry event structure.

    FRD: Never includes raw payloads, names, paths, prompts, error messages,
    or any customer/user-identifiable information.
    """

    category: TelemetryCategory
    session_id: SessionId
    timestamp: Timestamp
    feature_area: str  # from fixed taxonomy, never free-form names
    operation_type: str  # from fixed taxonomy
    outcome_category: str  # success/failure/rejected/cancelled/timeout
    version: VersionString = "unknown"
    platform: PlatformName = "unknown"
    duration_bucket: float | None = None
    metadata: dict[str, str] | None = None  # coarse metadata only, no PII
