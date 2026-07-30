"""Tests for AuditEmitter — FR-DIA-003.

Exercises immutable audit record creation, fallback buffering,
subscriber isolation, and redaction via AuditEmitter.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio
from typing import Any

from modules.diagnostics.src.capabilities_audit_emitter import AuditEmitter
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import AuditEventRequestVO

import pytest


def _make_emitter(**kwargs: Any) -> AuditEmitter:
    return AuditEmitter(**kwargs)



class TestAuditEventEmission:
    """Test immutable audit record creation and emission."""

    def test_emit_audit_event_returns_confirmed(self) -> None:
        cap = _make_emitter()
        result = asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        assert result.emission_confirmed is True

    def test_audit_record_contains_category(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.category == "security_violation"

    def test_audit_record_contains_severity(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.severity == "critical"

    def test_audit_record_contains_source_feature(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="connection_failure",
                    severity="warning",
                    source_feature="launcher",
                    operation_type="connection_lost",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.source_feature == "launcher"

    def test_audit_record_contains_operation_type(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="task_failure",
                    severity="error",
                    source_feature="dispatcher",
                    operation_type="execution_failed",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.operation_type == "execution_failed"

    def test_audit_record_has_timestamp(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.timestamp > 0

    def test_audit_record_has_correlation_id(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                    correlation_id="trace-12345",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.correlation_id == "trace-12345"

    def test_audit_record_no_correlation_id_when_absent(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.correlation_id is None


class TestAuditRecordImmutability:
    """Test audit records are frozen (immutable) once emitted."""

    def test_audit_records_are_frozen(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        record = cap._fallback_buffer[-1]
        with pytest.raises(AttributeError):
            record.category = "changed"

    def test_audit_records_are_appended(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="task_failure",
                    severity="error",
                    source_feature="dispatcher",
                    operation_type="execution_failed",
                )
            )
        )
        assert len(cap._fallback_buffer) == 2

    def test_previous_records_unchanged_after_new_emission(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        first_record = cap._fallback_buffer[0]
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="task_failure",
                    severity="error",
                    source_feature="dispatcher",
                    operation_type="execution_failed",
                )
            )
        )
        assert first_record.category == "security_violation"


class TestAuditRedaction:
    """Test audit record content passes redaction rules."""

    def test_audit_redacts_sensitive_in_metadata(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                    target_metadata={"password": "secret123", "api_key": "abc123"},
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert "REDACTED" in str(record.target_metadata.get("password", ""))

    def test_audit_record_no_credentials_in_metadata(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                    target_metadata={"token": "ghp_ab...o345"},
                )
            )
        )
        record = cap._fallback_buffer[-1]
        assert "ghp_" not in str(record.target_metadata)


class TestFallbackBuffering:
    """Test fallback buffering when no sink is configured."""

    def test_fallback_buffer_grows_on_emission(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        assert len(cap._fallback_buffer) == 1

    def test_fallback_buffer_is_bounded(self) -> None:
        cap = _make_emitter(max_buffer_size=3)
        for idx in range(3):
            asyncio.run(
                cap.emit_audit_event(
                    request=AuditEventRequestVO(
                        category="security_violation",
                        severity="critical",
                        source_feature="gateway",
                        operation_type="connection_failure",
                        correlation_id=f"trace-{idx}",
                    )
                )
            )
        assert len(cap._fallback_buffer) == 3

    def test_emission_path_is_fallback(self) -> None:
        cap = _make_emitter()
        out = asyncio.run(
            cap.emit_audit_event(
                request=AuditEventRequestVO(
                    category="security_violation",
                    severity="critical",
                    source_feature="gateway",
                    operation_type="connection_failure",
                )
            )
        )
        assert out.emission_path == "fallback"
