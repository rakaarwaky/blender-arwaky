"""Capability: Telemetry event recorder.

Implements TelemetryRecordingProtocol — captures anonymous usage records
with PII-free schema. Consent must be active; withdrawal stops immediately.

FR-TLM-001: Record Anonymous Usage Event
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    SessionId,
    Timestamp,
)
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_recording_protocol import (
    TelemetryRecordingProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)

logger = logging.getLogger("BlenderMCPServer")

# Allowlist of action types that may be recorded
ALLOWED_ACTIONS: set[str] = {
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
}

# Feature area taxonomy
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


class TelemetryRecordingCapability(TelemetryRecordingProtocol):
    """Business logic for recording anonymous telemetry events."""

    def __init__(
        self,
        session_protocol: TelemetrySessionProtocol,
        classification_protocol: TelemetryClassificationProtocol,
        buffer_capacity: int = 1000,
    ) -> None:
        """Initialize with dependent protocols.

        Args:
            session_protocol: Protocol for session ID management.
            classification_protocol: Protocol for event classification.
            buffer_capacity: Maximum buffered records before drop-oldest.
        """
        self._session_protocol = session_protocol
        self._classification_protocol = classification_protocol
        self._buffer_capacity = buffer_capacity
        self._buffer: list[dict[str, Any]] = []

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
        # Consent check — nothing recorded if consent inactive
        if not consent_active:
            return {"recorded": False, "reason": "consent_inactive"}

        # Action allowlist check
        if action_type not in ALLOWED_ACTIONS:
            return {"recorded": False, "reason": "action_not_in_allowlist"}

        # Classify event
        classified = await self._classification_protocol.classify_event(
            action_type, feature_area
        )

        # Get session ID
        session_id = await self._session_protocol.get_session_id(
            consent_active=consent_active
        )

        # Build anonymous record (PII-free)
        record: dict[str, Any] = {
            "timestamp": Timestamp(self._current_timestamp()),
            "action_type": action_type,
            "session_id": SessionId(str(session_id)),
            "feature_area": classified.get("feature_area", feature_area or "other"),
            "operation_type": classified.get("operation_type", "other"),
            "outcome_category": outcome_category,
            "duration_bucket": duration_bucket,
        }

        # Buffer with backpressure (drop oldest if full)
        self._buffer.append(record)
        if len(self._buffer) > self._buffer_capacity:
            self._buffer = self._buffer[-self._buffer_capacity:]

        return {
            "recorded": True,
            "session_id": str(session_id),
            "feature_area": record["feature_area"],
            "operation_type": record["operation_type"],
        }

    def _current_timestamp(self) -> float:
        """Return current Unix timestamp."""
        import time
        return time.time()
