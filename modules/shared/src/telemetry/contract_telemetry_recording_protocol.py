"""Telemetry domain contract: event recording protocol (ABC based).

FR-TLM-001: Record Anonymous Usage Event
Consent must be active; withdrawal stops immediately.
PII scrubbing at ingestion before buffering.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import EnabledFlag, SuccessFlag
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    RecordingResult,
    TelemetryDraft,
)


class TelemetryRecordingProtocol(ABC):
    """Sync protocol for recording anonymous usage events without PII."""

    @abstractmethod
    def record_event(
        self,
        draft: TelemetryDraft,
        consent_active: EnabledFlag,
    ) -> RecordingResult:
        """Capture a single anonymous usage record.

        FR-TLM-001: Nothing recorded unless consent is active.
        PII scrubbing applies at ingestion before buffering.

        Args:
            draft: Fully composed telemetry draft from orchestrator.
            consent_active: Whether telemetry consent is enabled.

        Returns:
            RecordingResult with acknowledgment or rejection reason.
        """
        ...

    @abstractmethod
    def is_enabled(self) -> SuccessFlag:
        """Check if telemetry consent is active."""
        ...
