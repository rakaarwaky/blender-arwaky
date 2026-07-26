"""Agent: Telemetry feature orchestrator.

Coordinates telemetry event recording, classification, session management,
and enrichment across all capability layers.
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    Details,
    DurationMs,
    ErrorMessage,
    SuccessFlag,
    ToolName,
)
from modules.gateway.src import IBlenderConnectionProtocol
from modules.shared.src.telemetry.contract_telemetry_classification import (
    TelemetryClassificationPort,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment import (
    TelemetryEnrichmentPort,
)
from modules.shared.src.telemetry.contract_telemetry_recording import (
    TelemetryRecordingPort,
)
from modules.shared.src.telemetry.contract_telemetry_session_management import (
    TelemetrySessionManagementPort,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import EventType

logger = logging.getLogger("BlenderMCPServer")


class TelemetryOrchestrator:
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
        event_type = self._classifier.classify_event(raw_type="startup")
        # Record with session ID and enrichment
        self._recorder.record_event(event_type=event_type)
        logger.debug("Startup event recorded")

    def record_action_execution(
        self,
        action_name: str,
        success: bool,
        duration_ms: float,
    ) -> None:
        """Record an action execution event (FR-TLM-001, FR-TLM-002)."""
        # Classify the event
        event_type = self._classifier.classify_event(
            tool_name=ToolName(action_name)
        )
        # Record with metrics
        self._recorder.record_event(
            event_type=event_type,
            success=SuccessFlag(success),
            duration_ms=DurationMs(duration_ms),
        )
        logger.debug("Action execution event recorded: %s", action_name)

    def record_system_error(self, error_category: str, context: str) -> None:
        """Record a system error event (FR-TLM-001, FR-TLM-002)."""
        # Classify the event
        event_type = self._classifier.classify_event(error_message=ErrorMessage(context))
        # Record with error details
        self._recorder.record_event(event_type=event_type)
        logger.debug("System error event recorded: %s", error_category)

    def get_session_id(self) -> str:
        """Get the current session identifier (FR-TLM-003)."""
        session_id = self._session_manager.get_session_id()
        return str(session_id)

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
            "metadata": str(metadata) if metadata else {},
        }
