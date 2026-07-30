"""Root: Telemetry feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
telemetry module: Capabilities → Agent Orchestrator → (exposed as TelemetryOrchestrator).

This file is the composition root for the telemetry feature.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import FilePath, VersionString

from .agent_telemetry_orchestrator import TelemetryOrchestrator
from .capabilities_telemetry_classifier import TelemetryEventClassifier
from .capabilities_telemetry_enricher import TelemetryEventEnricher
from .capabilities_telemetry_recorder import TelemetryRecordingCapability
from .capabilities_telemetry_session_manager import TelemetrySessionManager

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryContainer:
    def __init__(
        self,
        session_path: FilePath,
        app_version: VersionString | None = None,
    ) -> None:
        self._session_path = session_path
        self._app_version = app_version
        self._orchestrator: TelemetryOrchestrator | None = None
        self._wired = False

    def wire(self) -> None:
        if self._wired:
            return

        classifier = TelemetryEventClassifier()
        session_manager = TelemetrySessionManager(self._session_path)
        enricher = TelemetryEventEnricher(self._app_version)
        recorder = TelemetryRecordingCapability()

        self._orchestrator = TelemetryOrchestrator(
            recorder=recorder,
            classifier=classifier,
            session_manager=session_manager,
            enricher=enricher,
        )

        self._wired = True

    @property
    def agent(self) -> TelemetryOrchestrator:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("TelemetryContainer not wired — call wire() first")
        return self._orchestrator


def create_telemetry_feature(
    session_path: FilePath,
    app_version: VersionString | None = None,
) -> TelemetryOrchestrator:
    container = TelemetryContainer(session_path, app_version)
    container.wire()
    return container.agent
