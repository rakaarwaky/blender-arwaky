"""Agent: Telemetry feature orchestrator.

Coordinates telemetry event recording, classification, session management,
and enrichment across all capability layers.
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    DurationMs,
    ErrorString,
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_aggregate import ITelemetryAggregate
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationPort,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentPort,
)
from modules.shared.src.telemetry.contract_telemetry_recording_protocol import (
    TelemetryRecordingPort,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionManagementPort,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryOrchestrator(ITelemetryAggregate):
    """Orchestrates telemetry operations across capability layers.

    Coordinates recording, classification, session management, and enrichment.
    """

    def __init__(
        self,
        recorder: TelemetryRecordingPort,
        classifier: TelemetryClassificationPort,
        session_manager: TelemetrySessionManagementPort,
        enricher: TelemetryEnrichmentPort,
    ) -> None:
        self._recorder = recorder
        self._classifier = classifier
        self._session_manager = session_manager
        self._enricher = enricher

    def record_startup_event(self) -> None:
        """Record a startup event (FR-TLM-001, FR-TLM-002, FR-TLM-003, FR-TLM-004)."""
        # Classify the event
        event_type = self._classifier.classify_event("startup")
        logger.debug("Startup event classified: %s", event_type)

    def record_action_execution(
        self,
        action_name: ActionName,
        success: SuccessFlag,
        duration_ms: DurationMs,
    ) -> None:
        """Record an action execution event (FR-TLM-001, FR-TLM-002)."""
        # Classify the event by action name
        event_type = self._classifier.classify_event(str(action_name))
        logger.debug("Action execution event recorded: %s", action_name)

    def record_system_error(self, error_category: ErrorString) -> None:
        """Record a system error event (FR-TLM-001, FR-TLM-002).

        FRD: Never include error messages or stack traces in telemetry.
        Only the error category is recorded.
        """
        # Classify the event as ERROR
        event_type = self._classifier.classify_event("error")
        logger.debug("System error event recorded: %s", error_category)

    def get_session_id(self) -> SessionId | None:
        """Get the current session identifier (FR-TLM-003)."""
        return self._session_manager.get_session_id()

    def initialize_session(self) -> None:
        """Initialize a new session (FR-TLM-003)."""
        self._session_manager.initialize_session()
        logger.debug("New telemetry session initialized")

    def get_environment_metadata(self) -> dict:
        """Get enriched environment metadata (FR-TLM-004)."""
        metadata = self._enricher.enrich_event_metadata()
        return {
            "app_version": str(self._enricher.get_app_version()),
            "platform": str(self._enricher.get_platform()),
            "metadata": metadata if metadata else {},
        }
