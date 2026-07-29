"""Telemetry event type constants."""

from __future__ import annotations

from typing import Final

EVENT_TYPE_STARTUP: Final[str] = "startup"
EVENT_TYPE_TOOL_EXECUTION: Final[str] = "tool_execution"
EVENT_TYPE_PROMPT_SENT: Final[str] = "prompt_sent"
EVENT_TYPE_CONNECTION: Final[str] = "connection"
EVENT_TYPE_ERROR: Final[str] = "error"
