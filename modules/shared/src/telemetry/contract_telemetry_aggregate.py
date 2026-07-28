"""Aggregate contract for the telemetry feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_telemetry_classification import TelemetryClassificationPort
from .contract_telemetry_classification_protocol import TelemetryClassificationProtocol
from .contract_telemetry_enrichment import TelemetryEnrichmentPort
from .contract_telemetry_enrichment_protocol import TelemetryEnrichmentProtocol
from .contract_telemetry_recording import TelemetryRecordingPort
from .contract_telemetry_recording_protocol import TelemetryRecordingProtocol
from .contract_telemetry_session_management import TelemetrySessionManagementPort
from .contract_telemetry_session_protocol import TelemetrySessionProtocol

__all__ = [
    "TelemetryClassificationPort",
    "TelemetryClassificationProtocol",
    "TelemetryEnrichmentPort",
    "TelemetryEnrichmentProtocol",
    "TelemetryRecordingPort",
    "TelemetryRecordingProtocol",
    "TelemetrySessionManagementPort",
    "TelemetrySessionProtocol",
]
