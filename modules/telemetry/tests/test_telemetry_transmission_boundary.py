from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    EnabledFlag,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ClassificationResult,
    FeatureArea,
    OperationType,
    OutcomeCategory,
    SessionId,
    TelemetryCategory,
    TelemetryDraft,
)
from modules.telemetry.src.capabilities_telemetry_enricher import TelemetryEventEnricher
from modules.telemetry.src.capabilities_telemetry_recorder import TelemetryRecordingCapability
from modules.telemetry.src.capabilities_telemetry_transmission import (
    TelemetryTransmissionCapability,
)


def _draft() -> TelemetryDraft:
    return TelemetryDraft(
        action_type=ActionName("action_execute"),
        classification=ClassificationResult(
            category=TelemetryCategory.TOOL_EXECUTION,
            feature_area=FeatureArea("dispatcher"),
            operation_type=OperationType("execute"),
            outcome_category=OutcomeCategory("success"),
        ),
        session_id=SessionId("anonymous-session"),
        outcome_category=OutcomeCategory("success"),
    )


def test_recorder_uses_enricher_environment_metadata() -> None:
    enricher = TelemetryEventEnricher(app_version="2.4")
    recorder = TelemetryRecordingCapability(enricher=enricher)

    result = recorder.record_event(_draft(), EnabledFlag(True))

    assert result.recorded is True
    record = recorder._buffer[0]
    metadata = enricher.get_environment_metadata()
    assert record.version == metadata.app_version
    assert record.platform == metadata.platform
    assert metadata.schema_version == "1.0"


def test_transmission_is_explicitly_disabled_without_sender() -> None:
    result = TelemetryTransmissionCapability().transmit([])
    assert result.transmitted is True
    assert result.attempted is False

    result = TelemetryTransmissionCapability().transmit([object()])  # type: ignore[list-item]
    assert result.transmitted is False
    assert result.attempted is False
    assert result.error == "transmission_not_configured"


def test_transmission_sender_receives_scrubbed_records() -> None:
    received: list[object] = []
    capability = TelemetryTransmissionCapability(received.extend)
    source = TelemetryRecordingCapability(enricher=TelemetryEventEnricher())
    source.record_event(_draft(), EnabledFlag(True))

    result = capability.transmit(list(source._buffer))

    assert result.transmitted is True
    assert result.attempted is True
    assert len(received) == 1
    assert len(source._buffer) == 1


def test_transmission_failure_is_masked() -> None:
    def fail(_records: object) -> None:
        raise RuntimeError("secret transport detail")

    result = TelemetryTransmissionCapability(fail).transmit([object()])  # type: ignore[list-item]

    assert result.transmitted is False
    assert result.attempted is True
    assert result.error == "transmission_failed"
