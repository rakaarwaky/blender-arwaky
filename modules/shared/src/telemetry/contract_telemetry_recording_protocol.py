"""Telemetry domain contract: event recording protocol (ABC based).

Defines the protocol for capturing anonymous usage records with PII-free
schema. Consent must be active; withdrawal stops immediately.

FR-TLM-001: Record Anonymous Usage Event
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ActionName, SuccessFlag


class TelemetryRecordingProtocol(ABC):
    """Protocol for recording anonymous usage events without PII."""

    @abstractmethod
    async def record_event(
        self,
        action_type: ActionName,
        feature_area: str,
        outcome_category: str,
        consent_active: bool = True,
        duration_bucket: float | None = None,
    ) -> SuccessFlag:
        """Capture a single anonymous usage record.

        FR-TLM-001: Nothing recorded unless consent is active.
        PII scrubbing applies at ingestion before buffering.
        Records never contain raw payloads, file names, paths, or error messages.

        Args:
            action_type: The type of user action.
            feature_area: Product surface area (object, scene, render, etc.).
            outcome_category: success, failure, or rejected.
            consent_active: Whether telemetry consent is enabled.
            duration_bucket: Optional coarse duration bucket.

        Returns:
            Dict with recording acknowledgment and buffered record summary.
        """
        pass

# --- Merged from contract_telemetry_recording.py ---

"""
Contract: Port interface for telemetry collection.

Defines the contract for anonymous telemetry recording, configuration, and
decorator utilities. Single port for all telemetry-related concerns.
AES Port layer — depends only on taxonomy entities.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from ..common.taxonomy_core_vo import BlenderVersion, Details, DurationMs, ErrorMessage, Prompt, SuccessFlag, ToolName
from ..telemetry.taxonomy_telemetry_event import EventType


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
    ):
        """Record a telemetry event."""
        pass

    @abstractmethod
    def is_enabled(self) -> SuccessFlag:
        """Check if telemetry is currently enabled."""
        pass

    @abstractmethod
    def create_tool_decorator(self, tool_name: ToolName) -> Callable[..., Any]:
        """Create a decorator that records telemetry for an MCP tool."""
        pass
