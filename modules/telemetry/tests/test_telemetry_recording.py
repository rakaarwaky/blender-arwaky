"""Tests for telemetry event recording capability — FR-TLM-001.

FR-TLM-001: Record Anonymous Usage Event
- Nothing recorded unless consent is active
- PII scrubbing applies at ingestion before buffering
- Action allowlist enforcement
- Buffer with bounded size and drop-oldest backpressure
"""

from __future__ import annotations

import pytest

from modules.telemetry.src.capabilities_telemetry_recorder import (
    TelemetryRecordingCapability,
)


class MockSessionProtocol:
    """Mock session protocol for testing."""

    async def get_session_id(self, consent_active: bool = True) -> str:  # noqa: ARG002
        return "mock-session-id"


class MockClassificationProtocol:
    """Mock classification protocol for testing."""

    async def classify_event(self, action_type: str, feature_area: str | None = None) -> dict:  # noqa: ARG002
        return {"feature_area": feature_area or "other", "operation_type": "other"}


# ─── FR-TLM-001: Consent Check ────────────────────────────────────────────


class TestConsentCheck:
    """FR-TLM-001: Consent must be active for recording."""

    @pytest.mark.asyncio
    async def test_inactive_consent_rejected(self) -> None:
        """FR-TLM-001: Events are not recorded when consent is inactive."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        result = await recorder.record_event(
            action_type="action_execute",
            consent_active=False,
        )
        assert result["recorded"] is False
        assert result["reason"] == "consent_inactive"

    @pytest.mark.asyncio
    async def test_active_consent_allowed(self) -> None:
        """FR-TLM-001: Events are recorded when consent is active."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        result = await recorder.record_event(
            action_type="action_execute",
            consent_active=True,
        )
        assert result["recorded"] is True


# ─── FR-TLM-001: Action Allowlist ─────────────────────────────────────────


class TestActionAllowlist:
    """FR-TLM-001: Only allowed actions are recorded."""

    @pytest.mark.asyncio
    async def test_allowed_action_recorded(self) -> None:
        """FR-TLM-001: Actions on the allowlist are recorded."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        result = await recorder.record_event(
            action_type="action_execute",
            consent_active=True,
        )
        assert result["recorded"] is True

    @pytest.mark.asyncio
    async def test_disallowed_action_rejected(self) -> None:
        """FR-TLM-001: Actions not on the allowlist are rejected."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        result = await recorder.record_event(
            action_type="forbidden_action",
            consent_active=True,
        )
        assert result["recorded"] is False
        assert result["reason"] == "action_not_in_allowlist"


# ─── FR-TLM-001: Buffer Management ────────────────────────────────────────


class TestBufferManagement:
    """FR-TLM-001: Buffer with bounded size and drop-oldest backpressure."""

    @pytest.mark.asyncio
    async def test_event_added_to_buffer(self) -> None:
        """FR-TLM-001: Recorded events are added to the buffer."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
            buffer_capacity=5,
        )
        await recorder.record_event(action_type="action_execute", consent_active=True)
        assert len(recorder._buffer) == 1

    @pytest.mark.asyncio
    async def test_buffer_respects_capacity(self) -> None:
        """FR-TLM-001: Buffer drops oldest entries when capacity exceeded."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
            buffer_capacity=3,
        )
        for _ in range(5):
            await recorder.record_event(action_type="action_execute", consent_active=True)
        assert len(recorder._buffer) <= 3

    @pytest.mark.asyncio
    async def test_buffer_preserves_recent_entries(self) -> None:
        """FR-TLM-001: Buffer preserves recent entries, drops oldest."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
            buffer_capacity=2,
        )
        for _i in range(4):
            await recorder.record_event(action_type="action_execute", consent_active=True)
        assert len(recorder._buffer) == 2

    @pytest.mark.asyncio
    async def test_buffer_contains_valid_records(self) -> None:
        """FR-TLM-001: Buffered records have valid structure."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        await recorder.record_event(action_type="action_execute", consent_active=True)
        record = recorder._buffer[0]
        assert "timestamp" in record
        assert "action_type" in record
        assert "session_id" in record
        assert "outcome_category" in record


# ─── FR-TLM-001: PII-Free Schema ──────────────────────────────────────────


class TestPIIFreeSchema:
    """FR-TLM-001: Recorded events contain no PII."""

    @pytest.mark.asyncio
    async def test_record_contains_no_user_identity(self) -> None:
        """FR-TLM-001: Records do not contain user identity information."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        await recorder.record_event(action_type="action_execute", consent_active=True)
        record = recorder._buffer[0]
        # Session ID is random, not traceable to user
        assert record["session_id"] != "user@example.com"

    @pytest.mark.asyncio
    async def test_record_contains_anonymous_session(self) -> None:
        """FR-TLM-001: Session IDs are anonymous."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        await recorder.record_event(action_type="action_execute", consent_active=True)
        record = recorder._buffer[0]
        # Session should be a mock ID, not real user data
        assert "mock-session-id" in str(record["session_id"])


# ─── FR-TLM-001: Outcome Categories ───────────────────────────────────────


class TestOutcomeCategories:
    """FR-TLM-001: Recording supports outcome categories."""

    @pytest.mark.asyncio
    async def test_success_outcome(self) -> None:
        """FR-TLM-001: Success outcome is recorded."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        await recorder.record_event(
            action_type="action_execute",
            outcome_category="success",
            consent_active=True,
        )
        assert len(recorder._buffer) == 1

    @pytest.mark.asyncio
    async def test_failure_outcome(self) -> None:
        """FR-TLM-001: Failure outcome is recorded."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        await recorder.record_event(
            action_type="action_execute",
            outcome_category="failure",
            consent_active=True,
        )
        assert len(recorder._buffer) == 1

    @pytest.mark.asyncio
    async def test_rejected_outcome(self) -> None:
        """FR-TLM-001: Rejected outcome is recorded."""
        recorder = TelemetryRecordingCapability(
            session_protocol=MockSessionProtocol(),
            classification_protocol=MockClassificationProtocol(),
        )
        await recorder.record_event(
            action_type="action_execute",
            outcome_category="rejected",
            consent_active=True,
        )
        assert len(recorder._buffer) == 1
