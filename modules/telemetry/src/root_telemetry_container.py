"""Root: Telemetry feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
telemetry module: Capabilities → Agent Orchestrator → (exposed as TelemetryOrchestrator).

This file is the composition root for the telemetry feature.

Wiring order matters: the recorder depends on the session and classification
protocols, so those two capabilities are built first and injected into the
recorder before all four are handed to the orchestrator.
"""

from __future__ import annotations

import logging

from .agent_orchestrator import TelemetryOrchestrator
from .capabilities_telemetry_classification import TelemetryEventClassifier
from .capabilities_telemetry_enrichment import TelemetryEventEnricher
from .capabilities_telemetry_recorder import TelemetryRecordingCapability
from .capabilities_telemetry_session_management import TelemetrySessionManager

logger = logging.getLogger("BlenderMCPServer")


class TelemetryContainer:
    """Dependency injection container for the telemetry feature module.

    Wires the four telemetry capabilities to the orchestrator.
    """

    def __init__(self) -> None:
        self._orchestrator: TelemetryOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire telemetry capabilities to the orchestrator."""
        if self._wired:
            return

        logger.info("Wiring telemetry feature module")

        classifier = TelemetryEventClassifier()
        session_manager = TelemetrySessionManager()
        enricher = TelemetryEventEnricher()
        # Recorder depends on session + classification protocols.
        recorder = TelemetryRecordingCapability(
            session_protocol=session_manager,
            classification_protocol=classifier,
        )

        self._orchestrator = TelemetryOrchestrator(
            recorder=recorder,
            classifier=classifier,
            session_manager=session_manager,
            enricher=enricher,
        )

        self._wired = True
        logger.info("Telemetry feature module wired successfully")

    @property
    def agent(self) -> TelemetryOrchestrator:
        """Return the assembled telemetry orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("TelemetryContainer not wired — call wire() first")
        return self._orchestrator


def create_telemetry_feature() -> TelemetryOrchestrator:
    """Factory function to create and wire the telemetry feature module."""
    container = TelemetryContainer()
    container.wire()
    return container.agent
