"""Telemetry event type enumeration."""

from __future__ import annotations

from enum import Enum


class EventType(Enum):
    """Types of telemetry events."""

    STARTUP = "startup"
    TOOL_EXECUTION = "tool_execution"
    PROMPT_SENT = "prompt_sent"
    CONNECTION = "connection"
    ERROR = "error"
