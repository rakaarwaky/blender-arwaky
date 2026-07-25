"""Telemetry domain contract: telemetry recording port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from ..common.taxonomy_core_vo import (
    BlenderVersion,
    Details,
    DurationMs,
    ErrorMessage,
    Prompt,
    SuccessFlag,
    ToolName,
)
from .taxonomy_telemetry_event import EventType


class TelemetryRecordingPort(ABC):
    """Port interface for telemetry collection, configuration, and decorators."""

    @abstractmethod
    def record_event(
        self,
        event_type: EventType,
        tool_name: ToolName | None = None,
        prompt_text: Prompt | None = None,
        success: SuccessFlag | None = None,
        duration_ms: DurationMs | None = None,
        error_message: ErrorMessage | None = None,
        blender_version: BlenderVersion | None = None,
        metadata: Details | None = None,
    ) -> None:
        """Record a telemetry event."""
        pass

    @abstractmethod
    def is_enabled(self) -> SuccessFlag:
        """Check if telemetry is currently enabled."""
        pass

    @abstractmethod
    def create_tool_decorator(
        self, tool_name: ToolName
    ) -> Callable[..., Any]:
        """Create a decorator that records telemetry for an MCP tool."""
        pass
