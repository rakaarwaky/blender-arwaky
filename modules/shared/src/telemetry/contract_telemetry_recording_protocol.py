"""Telemetry domain contract: event recording protocol (ABC based).

FR-TLM-001: Record Anonymous Usage Event
Consent must be active; withdrawal stops immediately.
PII scrubbing at ingestion before buffering.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import SuccessFlag


class TelemetryRecordingProtocol(ABC):
    """Async protocol for recording anonymous usage events without PII."""

    @abstractmethod
    async def record_event(
        self,
        action_type: str,
        feature_area: str | None = None,
        outcome_category: str = "success",
        consent_active: bool = True,
        duration_bucket: float | None = None,
    ) -> dict[str, Any]:
        """Capture a single anonymous usage record.

        FR-TLM-001: Nothing recorded unless consent is active.
        PII scrubbing applies at ingestion before buffering.

        Args:
            action_type: The type of user action.
            feature_area: Product surface area.
            outcome_category: success, failure, or rejected.
            consent_active: Whether telemetry consent is enabled.
            duration_bucket: Optional coarse duration bucket.

        Returns:
            Dict with recording acknowledgment and buffered record summary.
        """
        ...


class TelemetryRecordingPort(ABC):
    """Sync facade for orchestrator consumption."""

    @abstractmethod
    async def record_event(
        self,
        event_type: str,
        consent_active: bool = True,
    ) -> dict[str, Any]:
        """Record event via port (delegates to protocol impl)."""
        ...

    @abstractmethod
    async def is_enabled(self) -> SuccessFlag:
        """Check if telemetry consent is active."""
        ...
