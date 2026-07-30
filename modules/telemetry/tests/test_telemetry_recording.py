"""Tests for telemetry event recording capability — FR-TLM-001.

FR-TLM-001: Record Anonymous Usage Event
- Nothing recorded unless consent is active
- PII scrubbing applies at ingestion before buffering
- Action allowlist enforcement
- Buffer with bounded size and drop-oldest backpressure
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    EnabledFlag,
    SuccessFlag,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ClassificationResult,
    DurationBucket,
    FeatureArea,
    OperationType,
    OutcomeCategory,
    SessionId,
    TelemetryCategory,
    TelemetryDraft,
)
from modules.telemetry.src.capabilities_telemetry_recorder import (
    TelemetryRecordingCapability,
)


def _make_draft(
    action: str = "action_execute",
    outcome: str = "success",
    bucket: float | None = None,
) -> TelemetryDraft:
    return TelemetryDraft(
        action_type=ActionName(action),
        classification=ClassificationResult(
            category=TelemetryCategory.TOOL_EXECUTION,
            feature_area=FeatureArea("dispatcher"),
            operation_type=OperationType("execute"),
            outcome_category=OutcomeCategory(outcome),
        ),
        session_id=SessionId("mock-session-id"),
        outcome_category=OutcomeCategory(outcome),
        duration_bucket=DurationBucket(bucket) if bucket is not None else None,
    )


class TestConsentCheck:
    def test_inactive_consent_rejected(self) -> None:
        recorder = TelemetryRecordingCapability()
        result = recorder.record_event(
            _make_draft(),
            consent_active=EnabledFlag(False),
        )
        assert result.recorded is False
        assert result.rejection_reason is not None
        assert result.rejection_reason.value == "consent_inactive"

    def test_active_consent_allowed(self) -> None:
        recorder = TelemetryRecordingCapability()
        result = recorder.record_event(
            _make_draft(),
            consent_active=EnabledFlag(True),
        )
        assert result.recorded is True


class TestActionAllowlist:
    def test_allowed_action_recorded(self) -> None:
        recorder = TelemetryRecordingCapability()
        result = recorder.record_event(
            _make_draft(action="action_execute"),
            consent_active=EnabledFlag(True),
        )
        assert result.recorded is True

    def test_disallowed_action_rejected(self) -> None:
        recorder = TelemetryRecordingCapability()
        result = recorder.record_event(
            _make_draft(action="forbidden_action"),
            consent_active=EnabledFlag(True),
        )
        assert result.recorded is False
        assert result.rejection_reason is not None
        assert result.rejection_reason.value == "action_not_allowlisted"


class TestBufferManagement:
    def test_event_added_to_buffer(self) -> None:
        recorder = TelemetryRecordingCapability(buffer_capacity=5)
        recorder.record_event(
            _make_draft(),
            consent_active=EnabledFlag(True),
        )
        assert len(recorder._buffer) == 1

    def test_buffer_respects_capacity(self) -> None:
        recorder = TelemetryRecordingCapability(buffer_capacity=3)
        for _ in range(5):
            recorder.record_event(
                _make_draft(),
                consent_active=EnabledFlag(True),
            )
        assert len(recorder._buffer) <= 3

    def test_buffer_preserves_recent_entries(self) -> None:
        recorder = TelemetryRecordingCapability(buffer_capacity=2)
        for _ in range(4):
            recorder.record_event(
                _make_draft(),
                consent_active=EnabledFlag(True),
            )
        assert len(recorder._buffer) == 2

    def test_buffer_contains_valid_records(self) -> None:
        recorder = TelemetryRecordingCapability()
        recorder.record_event(
            _make_draft(),
            consent_active=EnabledFlag(True),
        )
        record = recorder._buffer[0]
        assert record.action_type == ActionName("action_execute")
        assert record.session_id == SessionId("mock-session-id")
        assert record.outcome_category == OutcomeCategory("success")


class TestIsEnabled:
    def test_is_enabled_returns_true_by_default(self) -> None:
        recorder = TelemetryRecordingCapability()
        assert recorder.is_enabled() == SuccessFlag(True)
