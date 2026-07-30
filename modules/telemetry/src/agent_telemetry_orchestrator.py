"""Agent: Telemetry feature orchestrator.

Coordinates telemetry event recording, classification, session management,
and enrichment across all capability layers.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    DurationMs,
    EnabledFlag,
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_aggregate import ITelemetryAggregate
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_recording_protocol import (
    TelemetryRecordingProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    DurationBucket,
    EnvironmentMetadata,
    OutcomeCategory,
    TelemetryDraft,
    TelemetryErrorCategory,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryOrchestrator(ITelemetryAggregate):
    def __init__(
        self,
        recorder: TelemetryRecordingProtocol,
        classifier: TelemetryClassificationProtocol,
        session_manager: TelemetrySessionProtocol,
        enricher: TelemetryEnrichmentProtocol,
    ) -> None:
        self._recorder = recorder
        self._classifier = classifier
        self._session_manager = session_manager
        self._enricher = enricher

    def record_startup_event(self) -> None:
        self._record(ActionName("startup"), OutcomeCategory("success"), None)

    def record_action_execution(
        self,
        action_name: ActionName,
        success: SuccessFlag,
        duration_ms: DurationMs,
    ) -> None:
        outcome = OutcomeCategory("success" if bool(success) else "failure")
        bucket = DurationBucket(float(duration_ms))
        self._record(action_name, outcome, bucket)

    def record_system_error(
        self,
        error_category: TelemetryErrorCategory,
    ) -> None:
        self._record(
            ActionName(str(error_category)),
            OutcomeCategory("error"),
            None,
        )

    def get_session_id(self) -> SessionId | None:
        consent = self._recorder.is_enabled()
        return self._session_manager.get_session_id(EnabledFlag(bool(consent)))

    def initialize_session(self) -> None:
        self._session_manager.initialize_session()

    def get_environment_metadata(self) -> EnvironmentMetadata:
        return self._enricher.get_environment_metadata()

    def _record(
        self,
        action_type: ActionName,
        outcome: OutcomeCategory,
        duration_bucket: DurationBucket | None,
    ) -> None:
        try:
            consent = self._recorder.is_enabled()
            if not bool(consent):
                return

            session_id = self._session_manager.get_session_id(
                EnabledFlag(bool(consent))
            )
            if session_id is None:
                return

            classification = self._classifier.classify_event(action_type)
            draft = TelemetryDraft(
                action_type=action_type,
                classification=classification,
                session_id=session_id,
                outcome_category=outcome,
                duration_bucket=duration_bucket,
            )

            self._recorder.record_event(
                draft, EnabledFlag(bool(consent))
            )
        except Exception:
            logger.debug("Telemetry recording skipped due to internal failure")
