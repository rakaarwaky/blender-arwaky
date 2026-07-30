"""Telemetry feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/telemetry/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/telemetry/)   → 4 individual protocols + Aggregate ABC
  - Capabilities (4 executors)          → One per FR-TEL operation
  - Agent                               → TelemetryOrchestrator (Aggregate facade)
  - Root                                → TelemetryContainer (DI wiring)
"""

from .agent_telemetry_orchestrator import TelemetryOrchestrator
from .capabilities_telemetry_classifier import TelemetryEventClassifier
from .capabilities_telemetry_enricher import TelemetryEventEnricher
from .capabilities_telemetry_recorder import TelemetryRecordingCapability
from .capabilities_telemetry_session_manager import TelemetrySessionManager
from .root_telemetry_container import TelemetryContainer, create_telemetry_feature

__all__ = [
    "TelemetryEventClassifier",
    "TelemetryEventEnricher",
    "TelemetryOrchestrator",
    "TelemetryRecordingCapability",
    "TelemetrySessionManager",
    "TelemetryContainer",
    "create_telemetry_feature",
]
