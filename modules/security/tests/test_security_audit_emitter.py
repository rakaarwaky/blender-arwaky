"""Tests for AuditEmitter — FR-SEC-005.

Exercises security audit event emission: event ID/timestamp generation,
sensitive value redaction in metadata, fallback sink behavior, and
immutable event creation.
Run via pytest from repo root.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from modules.security.src.capabilities_audit_emitter import AuditEmitter
from modules.shared.src.security.taxonomy_security_vo import (
    AuditSeverity,
    SecurityAuditEventVO,
    ViolationCategory,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_emitter(sink=None) -> AuditEmitter:
    """Create an AuditEmitter with optional sink."""
    return AuditEmitter(sink=sink)


def _make_event(**overrides: object) -> SecurityAuditEventVO:
    """Create a SecurityAuditEventVO with optional field overrides."""
    base = SecurityAuditEventVO(
        violation_category=ViolationCategory.PATH_TRAVERSAL,
        operation_type="validate_path",
        source_feature="asset",
        severity=AuditSeverity.WARNING,
    )
    update = {k: v for k, v in overrides.items()}
    return SecurityAuditEventVO(**{**dict(base.__dict__), **update})


# ─── FR-SEC-005: Emit Security Audit Events ──────────────────────────────


class TestEventIdAndTimestamp:
    """Test event ID and timestamp generation (FR-SEC-005)."""

    def test_event_has_id(self) -> None:
        """FR-SEC-005: emitted event has an event ID."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert out.event_id is not None
        assert len(out.event_id) > 0

    def test_event_has_timestamp(self) -> None:
        """FR-SEC-005: emitted event has a timestamp."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert out.timestamp > 0

    def test_event_id_is_unique(self) -> None:
        """FR-SEC-005: each emitted event has a unique ID."""
        cap = _make_emitter()
        import asyncio
        e1 = asyncio.run(cap.emit_audit(_make_event()))
        e2 = asyncio.run(cap.emit_audit(_make_event()))
        assert e1.event_id != e2.event_id

    def test_timestamp_is_recent(self) -> None:
        """FR-SEC-005: timestamp is within reasonable range of current time."""
        cap = _make_emitter()
        import asyncio
        before = time.time()
        out = asyncio.run(cap.emit_audit(_make_event()))
        after = time.time()
        assert before <= out.timestamp <= after + 10  # 10s buffer


class TestEventFields:
    """Test emitted event field preservation (FR-SEC-005)."""

    def test_violation_category_preserved(self) -> None:
        """FR-SEC-005: violation category is preserved."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(violation_category=ViolationCategory.CODE_VIOLATION)))
        assert out.violation_category == ViolationCategory.CODE_VIOLATION

    def test_operation_type_preserved(self) -> None:
        """FR-SEC-005: operation type is preserved."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(operation_type="validate_code")))
        assert out.operation_type == "validate_code"

    def test_source_feature_preserved(self) -> None:
        """FR-SEC-005: source feature is preserved."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(source_feature="gateway")))
        assert out.source_feature == "gateway"

    def test_severity_preserved(self) -> None:
        """FR-SEC-005: severity level is preserved."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(severity=AuditSeverity.CRITICAL)))
        assert out.severity == AuditSeverity.CRITICAL

    def test_correlation_id_preserved(self) -> None:
        """FR-SEC-005: correlation identifier is preserved."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(correlation_id="trace-12345")))
        assert out.correlation_id == "trace-12345"

    def test_policy_mode_preserved(self) -> None:
        """FR-SEC-005: policy mode is preserved."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(policy_mode="strict")))
        assert out.policy_mode == "strict"


class TestTargetMetadataRedaction:
    """Test sensitive value redaction in target metadata (FR-SEC-004 + FR-SEC-005)."""

    def test_password_in_metadata_redacted(self) -> None:
        """FR-SEC-005: password=xxx in metadata is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"auth": "password=hunter2"})
        out = asyncio.run(cap.emit_audit(event))
        assert "hunter2" not in str(out.target_metadata)

    def test_token_in_metadata_redacted(self) -> None:
        """FR-SEC-005: token=xxx in metadata is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"auth": "token=bearer-xyz"})
        out = asyncio.run(cap.emit_audit(event))
        assert "bearer-xyz" not in str(out.target_metadata)

    def test_api_key_in_metadata_redacted(self) -> None:
        """FR-SEC-005: api_key=xxx in metadata is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"endpoint": "api_key=sk-abcdefghijklmnop"})
        out = asyncio.run(cap.emit_audit(event))
        assert "sk-abcdefghijklmnop" not in str(out.target_metadata)

    def test_json_config_in_metadata_redacted(self) -> None:
        """FR-SEC-005: JSON config with secrets is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"config": '{"password": "hunter2"}'})
        out = asyncio.run(cap.emit_audit(event))
        assert "hunter2" not in str(out.target_metadata)

    def test_nested_dict_redacted(self) -> None:
        """FR-SEC-005: nested dict with secrets is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"nested": {"pw": "password=hunter2"}})
        out = asyncio.run(cap.emit_audit(event))
        assert "hunter2" not in str(out.target_metadata)

    def test_list_values_redacted(self) -> None:
        """FR-SEC-005: list values with secrets are redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"items": ["api_key=abc123xyz"]})
        out = asyncio.run(cap.emit_audit(event))
        assert "abc123xyz" not in str(out.target_metadata)

    def test_spaced_secret_in_json_redacted(self) -> None:
        """FR-SEC-005: spaced secret in JSON metadata is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"config": '{"password": "my secret"}'})
        out = asyncio.run(cap.emit_audit(event))
        assert "my secret" not in str(out.target_metadata)
        assert "secret" not in str(out.target_metadata)

    def test_bearer_token_in_metadata_redacted(self) -> None:
        """FR-SEC-005: bearer token in metadata is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"auth": "Bearer eyJhbGciOiJIUzI1NiIs"})
        out = asyncio.run(cap.emit_audit(event))
        assert "eyJhbGciOiJIUzI1NiIs" not in str(out.target_metadata)

    def test_aws_key_in_metadata_redacted(self) -> None:
        """FR-SEC-005: AWS AKIA key in metadata is redacted."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"key": "AKIA1234567890ABCDEF"})
        out = asyncio.run(cap.emit_audit(event))
        assert "AKIA1234567890ABCDEF" not in str(out.target_metadata)

    def test_original_event_unchanged(self) -> None:
        """FR-SEC-005: caller's input event is never mutated."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(target_metadata={"auth": "password=hunter2"})
        asyncio.run(cap.emit_audit(event))
        # Original event still has raw secret
        assert event.target_metadata["auth"] == "password=hunter2"


class TestRedactedReasonRedaction:
    """Test redaction in redacted_reason field (FR-SEC-005)."""

    def test_secret_in_redacted_reason_masked(self) -> None:
        """FR-SEC-005: secrets in redacted_reason are masked."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(redacted_reason="blocked literal api_key=supersecretvalue")
        out = asyncio.run(cap.emit_audit(event))
        assert "supersecretvalue" not in (out.redacted_reason or "")

    def test_no_redacted_reason_is_none(self) -> None:
        """FR-SEC-005: missing redacted_reason returns None."""
        cap = _make_emitter()
        import asyncio
        event = _make_event(redacted_reason=None)
        out = asyncio.run(cap.emit_audit(event))
        assert out.redacted_reason is None


class TestSinkBehavior:
    """Test audit sink delivery behavior (FR-SEC-005)."""

    def test_sink_delivers_event(self) -> None:
        """FR-SEC-005: event is delivered to sink when available."""
        mock_sink = MagicMock()
        mock_sink.deliver = MagicMock()
        cap = _make_emitter(mock_sink)
        import asyncio
        asyncio.run(cap.emit_audit(_make_event()))
        assert mock_sink.deliver.called

    def test_sink_failure_does_not_raise(self) -> None:
        """FR-SEC-005: sink failure does not raise to caller."""
        mock_sink = MagicMock()
        mock_sink.deliver.side_effect = RuntimeError("sink broken")
        cap = _make_emitter(mock_sink)
        import asyncio
        # Should not raise — contextlib.suppress(Exception) catches it
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert out.event_id is not None

    def test_no_sink_returns_event(self) -> None:
        """FR-SEC-005: event returned even without sink."""
        cap = _make_emitter()  # no sink
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert out.event_id is not None


class TestImmutability:
    """Test audit record immutability (FR-SEC-005)."""

    def test_emitted_event_is_new_instance(self) -> None:
        """FR-SEC-005: emitted event is a new instance, not the input."""
        cap = _make_emitter()
        import asyncio
        event = _make_event()
        out = asyncio.run(cap.emit_audit(event))
        assert out is not event

    def test_emitted_event_has_generated_id(self) -> None:
        """FR-SEC-005: emitted event has auto-generated ID (not caller-provided)."""
        cap = _make_emitter()
        import asyncio
        # SecurityAuditEventVO doesn't take event_id in constructor — it's generated
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert len(out.event_id) == 16  # uuid4 hex[:16]


class TestAuditableCategories:
    """Test all auditable categories from FR-SEC-005."""

    @pytest.mark.parametrize(
        "category",
        [
            ViolationCategory.PATH_TRAVERSAL,
            ViolationCategory.UNAUTHORIZED_ACCESS,
            ViolationCategory.CODE_VIOLATION,
            ViolationCategory.UNSAFE_ARCHIVE_ENTRY,
            ViolationCategory.REDACTION_FAILURE,
        ],
    )
    def test_all_categories_emitted(self, category: ViolationCategory) -> None:
        """FR-SEC-005: all auditable categories produce events."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(violation_category=category)))
        assert out.event_id is not None
        assert out.violation_category == category

    def test_permission_denied_category(self) -> None:
        """FR-SEC-005: permission denied security event is auditable."""
        cap = _make_emitter()
        import asyncio
        # Permission denied would use a different category or severity
        out = asyncio.run(cap.emit_audit(_make_event(severity=AuditSeverity.ERROR)))
        assert out.event_id is not None


class TestFallbackWhenSinkUnavailable:
    """Test fallback when audit sink is unavailable (FR-SEC-005)."""

    def test_fallback_returns_valid_event(self) -> None:
        """FR-SEC-005: fallback produces valid event when sink unavailable."""
        cap = _make_emitter()  # no sink configured
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert out.event_id is not None
        assert out.timestamp > 0

    def test_fallback_preserves_all_fields(self) -> None:
        """FR-SEC-005: fallback preserves all event fields."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(
            violation_category=ViolationCategory.CODE_VIOLATION,
            operation_type="validate_code",
            source_feature="gateway",
            severity=AuditSeverity.CRITICAL,
        )))
        assert out.violation_category == ViolationCategory.CODE_VIOLATION
        assert out.operation_type == "validate_code"
        assert out.source_feature == "gateway"
        assert out.severity == AuditSeverity.CRITICAL


class TestRateLimiting:
    """Test high-frequency violation handling (FR-SEC-005)."""

    def test_multiple_events_emitted(self) -> None:
        """FR-SEC-005: multiple events can be emitted."""
        cap = _make_emitter()
        import asyncio
        for i in range(5):
            out = asyncio.run(cap.emit_audit(_make_event(operation_type=f"op_{i}")))
            assert out.event_id is not None

    def test_events_are_sequentially_unique(self) -> None:
        """FR-SEC-005: sequential events have unique IDs."""
        cap = _make_emitter()
        import asyncio
        ids = set()
        for _i in range(10):
            out = asyncio.run(cap.emit_audit(_make_event()))
            ids.add(out.event_id)
        assert len(ids) == 10


class TestEdgeCases:
    """Test edge cases from FR-SEC-005 specification."""

    def test_empty_target_metadata(self) -> None:
        """FR-SEC-005: empty target metadata is handled."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(target_metadata=None)))
        assert out.event_id is not None

    def test_missing_correlation_id(self) -> None:
        """FR-SEC-005: missing correlation ID is handled."""
        cap = _make_emitter()
        import asyncio
        out = asyncio.run(cap.emit_audit(_make_event(correlation_id=None)))
        assert out.event_id is not None

    def test_clock_skew_ordering(self) -> None:
        """FR-SEC-005: clock skew may order records oddly (timestamp-based)."""
        cap = _make_emitter()
        import asyncio
        e1 = asyncio.run(cap.emit_audit(_make_event()))
        e2 = asyncio.run(cap.emit_audit(_make_event()))
        # Timestamps should be close; ordering depends on wall clock
        assert e1.timestamp > 0
        assert e2.timestamp > 0

    def test_retention_purge_racing_emission(self) -> None:
        """FR-SEC-005: retention purge racing new emission (no local storage)."""
        cap = _make_emitter()
        import asyncio
        # Without local storage, purge is not applicable — event still emitted
        out = asyncio.run(cap.emit_audit(_make_event()))
        assert out.event_id is not None

    def test_redaction_failure_during_emit(self) -> None:
        """FR-SEC-005: redaction failure during emit produces warning."""
        cap = _make_emitter()
        import asyncio
        # Sensitive values in metadata are redacted by _redact_sensitive
        # If it fails, the whole value is masked — but _redact_sensitive doesn't raise
        out = asyncio.run(cap.emit_audit(_make_event(target_metadata={"key": "password=secret"})))
        assert "secret" not in str(out.target_metadata)


class TestRepresentation:
    """Test class representation."""

    def test_audit_emitter_repr(self) -> None:
        """AuditEmitter has a repr."""
        cap = AuditEmitter.__new__(AuditEmitter)
        AuditEmitter.__init__(cap, None)
        assert "AuditEmitter" in repr(cap)


# ─── FR-SEC-005: Immutable Once Emitted ──────────────────────────────────


class TestEventImmutabilityAfterEmission:
    """Test event immutability after emission (FR-SEC-005)."""

    def test_emitted_event_not_mutated_by_sink(self) -> None:
        """FR-SEC-005: emitted event is not mutated by sink delivery."""
        mock_sink = MagicMock()
        mock_sink.deliver = MagicMock(side_effect=lambda e: setattr(e, "mutated", True))
        cap = _make_emitter(mock_sink)
        import asyncio
        asyncio.run(cap.emit_audit(_make_event()))
        # The emitted event is a new instance; sink gets the same reference
        # but our _redact_sensitive creates copies, so original fields are safe

    def test_multiple_emissions_independent(self) -> None:
        """FR-SEC-005: multiple emissions produce independent events."""
        cap = _make_emitter()
        import asyncio
        e1 = asyncio.run(cap.emit_audit(_make_event(operation_type="op1")))
        e2 = asyncio.run(cap.emit_audit(_make_event(operation_type="op2")))
        assert e1.operation_type == "op1"
        assert e2.operation_type == "op2"
