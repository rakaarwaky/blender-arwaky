"""Capability: Telemetry event recorder.

Implements TelemetryRecordingProtocol — captures anonymous usage records
with PII-free schema. Consent must be active; withdrawal stops immediately.

FR-TLM-001: Record Anonymous Usage Event
PII scrubbing at ingestion before buffering.
"""

from __future__ import annotations

import logging
import time
from collections import deque

from modules.shared.src.common.taxonomy_core_vo import (
    EnabledFlag,
    PlatformName,
    SuccessFlag,
    Timestamp,
    VersionString,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_recording_protocol import (
    TelemetryRecordingProtocol,
)
from modules.shared.src.telemetry.taxonomy_event_constant import ALLOWED_ACTIONS
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    RecordingResult,
    TelemetryDraft,
    TelemetryRecord,
    TelemetryRejectionReason,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryRecordingCapability(TelemetryRecordingProtocol):
    def __init__(
        self,
        buffer_capacity: int = 1000,
        enricher: TelemetryEnrichmentProtocol | None = None,
    ) -> None:
        self._buffer: deque[TelemetryRecord] = deque(maxlen=buffer_capacity)
        self._enabled = EnabledFlag(True)
        self._enricher = enricher

    def is_enabled(self) -> SuccessFlag:
        return SuccessFlag(bool(self._enabled))

    def record_event(
        self,
        draft: TelemetryDraft,
        consent_active: EnabledFlag,
    ) -> RecordingResult:
        if not consent_active:
            return RecordingResult(
                recorded=SuccessFlag(False),
                rejection_reason=TelemetryRejectionReason.CONSENT_INACTIVE,
            )

        if str(draft.action_type) not in ALLOWED_ACTIONS:
            return RecordingResult(
                recorded=SuccessFlag(False),
                rejection_reason=TelemetryRejectionReason.ACTION_NOT_ALLOWLISTED,
            )

        metadata = self._enricher.get_environment_metadata() if self._enricher is not None else None
        record = TelemetryRecord(
            action_type=draft.action_type,
            category=draft.classification.category,
            session_id=draft.session_id,
            timestamp=Timestamp(time.time()),
            feature_area=draft.classification.feature_area,
            operation_type=draft.classification.operation_type,
            outcome_category=draft.outcome_category,
            version=metadata.app_version if metadata is not None else VersionString("unknown"),
            platform=metadata.platform if metadata is not None else PlatformName("unknown"),
            duration_bucket=draft.duration_bucket,
        )

        self._buffer.append(record)
        return RecordingResult(recorded=SuccessFlag(True))
