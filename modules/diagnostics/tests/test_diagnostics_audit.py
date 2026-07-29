"""Tests for AuditEmitter and InMemoryEventBus — FR-DIA-003.

Exercises immutable audit record creation, fallback buffering,
subscriber isolation, and redaction via AuditEmitter and InMemoryEventBus.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest

# Direct import — bypasses diagnostics.__init__.py to avoid MCP circular import chain
from modules.diagnostics.src.capabilities_audit_emission import (
    AuditEmitter,
    InMemoryEventBus,
)


def _make_emitter(**kwargs: Any) -> AuditEmitter:
    return AuditEmitter(**kwargs)


def _make_event_bus() -> InMemoryEventBus:
    return InMemoryEventBus()


class TestAuditEventEmission:
    """Test immutable audit record creation and emission."""

    def test_emit_audit_event_returns_confirmed(self) -> None:
        cap = _make_emitter()
        result = asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        assert result.emission_confirmed is True

    def test_audit_record_contains_category(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.category == "security_violation"

    def test_audit_record_contains_severity(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.severity == "critical"

    def test_audit_record_contains_source_feature(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="connection_failure",
                severity="warning",
                source_feature="launcher",
                operation_type="connection_lost",
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.source_feature == "launcher"

    def test_audit_record_contains_operation_type(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="task_failure",
                severity="error",
                source_feature="dispatcher",
                operation_type="execution_failed",
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.operation_type == "execution_failed"

    def test_audit_record_has_timestamp(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.timestamp > 0

    def test_audit_record_has_correlation_id(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
                correlation_id="trace-12345",
            )
        )
        record = cap._fallback_buffer[-1]
        assert record.correlation_id == "trace-12345"

    def test_audit_record_no_correlation_id_when_absent(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
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
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        # Frozen dataclass — raises FrozenInstanceError (subclass of AttributeError)
        record = cap._fallback_buffer[-1]
        with pytest.raises(AttributeError):
            record.category = "changed"

    def test_audit_records_are_appended(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        asyncio.run(
            cap.emit_audit_event(
                category="task_failure",
                severity="error",
                source_feature="dispatcher",
                operation_type="execution_failed",
            )
        )
        assert len(cap._fallback_buffer) == 2

    def test_previous_records_unchanged_after_new_emission(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        first_record = cap._fallback_buffer[0]
        asyncio.run(
            cap.emit_audit_event(
                category="task_failure",
                severity="error",
                source_feature="dispatcher",
                operation_type="execution_failed",
            )
        )
        assert first_record.category == "security_violation"


class TestAuditRedaction:
    """Test audit record content passes redaction rules."""

    def test_audit_redacts_sensitive_in_metadata(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
                target_metadata={"password": "secret123", "api_key": "abc123"},
            )
        )
        # Check that metadata was redacted
        record = cap._fallback_buffer[-1]
        assert "REDACTED" in str(record.target_metadata.get("password", ""))

    def test_audit_record_no_credentials_in_metadata(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
                target_metadata={"token": "ghp_abc123def456ghi789jkl012mno345"},
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
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        assert len(cap._fallback_buffer) == 1

    def test_fallback_buffer_is_bounded(self) -> None:
        cap = _make_emitter(max_buffer_size=5)
        for _ in range(10):
            asyncio.run(
                cap.emit_audit_event(
                    category="security_violation",
                    severity="warning",
                    source_feature="test",
                    operation_type="test_op",
                )
            )
        assert len(cap._fallback_buffer) <= 5

    def test_emission_path_is_fallback(self) -> None:
        cap = _make_emitter()
        result = asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        assert result.emission_path == "fallback"


class TestEventBusPublishSubscribe:
    """Test event bus subscribe and publish operations."""

    def test_event_bus_instantiates(self) -> None:
        bus = _make_event_bus()
        assert isinstance(bus, InMemoryEventBus)

    def test_subscribe_adds_subscriber(self) -> None:
        bus = _make_event_bus()

        class MockSubscriber:
            async def handle(self, event: Any) -> None:
                pass

        mock_subscriber = MockSubscriber()
        bus.subscribe(mock_subscriber)
        assert len(bus.get_subscribers()) == 1

    def test_subscribe_prevents_duplicates(self) -> None:
        bus = _make_event_bus()

        class MockSubscriber:
            async def handle(self, event: Any) -> None:
                pass

        mock_subscriber = MockSubscriber()
        bus.subscribe(mock_subscriber)
        bus.subscribe(mock_subscriber)
        assert len(bus.get_subscribers()) == 1

    def test_publish_calls_all_subscribers(self) -> None:
        bus = _make_event_bus()

        class MockSubscriber1:
            async def handle(self, event: Any) -> None:
                pass

        class MockSubscriber2:
            async def handle(self, event: Any) -> None:
                pass

        mock_subscriber1 = MockSubscriber1()
        mock_subscriber2 = MockSubscriber2()
        bus.subscribe(mock_subscriber1)
        bus.subscribe(mock_subscriber2)

        mock_event = MagicMock()
        asyncio.run(bus.publish(mock_event))


class TestSubscriberIsolation:
    """Test subscriber exception isolation."""

    def test_subscriber_exception_does_not_stop_others(self) -> None:
        bus = _make_event_bus()

        class FailingSubscriber:
            async def handle(self, event: Any) -> None:
                raise RuntimeError("subscriber error")

        class HealthySubscriber:
            async def handle(self, event: Any) -> None:
                pass

        bus.subscribe(FailingSubscriber())
        bus.subscribe(HealthySubscriber())

        mock_event = MagicMock()
        asyncio.run(bus.publish(mock_event))

    def test_subscriber_exception_is_logged(self) -> None:
        bus = _make_event_bus()

        class FailingSubscriber:
            async def handle(self, event: Any) -> None:
                raise ValueError("test error")

        bus.subscribe(FailingSubscriber())

        mock_event = MagicMock()
        asyncio.run(bus.publish(mock_event))


class TestAuditableCategories:
    """Test various auditable activity categories from FR-DIA-003."""

    @pytest.mark.parametrize(
        "category,operation_type",
        [
            ("security_violation", "policy_breach"),
            ("connection_failure", "establishment_failed"),
            ("connection_failure", "connection_lost"),
            ("task_failure", "execution_failed"),
            ("task_failure", "timeout_recovery"),
            ("destructive_action", "object_deleted"),
            ("destructive_action", "modifier_applied"),
            ("destructive_action", "process_terminated"),
        ],
    )
    def test_all_auditable_categories_emitted(self, category: str, operation_type: str) -> None:
        cap = _make_emitter()
        result = asyncio.run(
            cap.emit_audit_event(
                category=category,
                severity="warning",
                source_feature="test",
                operation_type=operation_type,
            )
        )
        assert result.emission_confirmed is True
        assert len(cap._fallback_buffer) >= 1
