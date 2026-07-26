"""Telemetry domain contract: event recording protocol (ABC based).

Defines the protocol for capturing anonymous usage records with PII-free
schema. Consent must be active; withdrawal stops immediately.

FR-TLM-001: Record Anonymous Usage Event
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TelemetryRecordingProtocol(ABC):
    """Protocol for recording anonymous usage events without PII."""

    @abstractmethod
    async def record_event(
        self,
        action_type: str,
        feature_area: str,
        outcome_category: str,
        consent_active: bool = True,
        duration_bucket: float | None = None,
    ) -> dict[str, Any]:
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
