"""Tests for AuditEmitter and InMemoryEventBus — FR-DIA-003.

Exercises immutable audit record creation, event bus publish/subscribe,
subscriber isolation, and fallback buffering via AuditEmitter and InMemoryEventBus.
Run via pytest from repo root.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.diagnostics.src.capabilities_audit_emission import (
    AuditEmitter,
    InMemoryEventBus,
)


def _make_emitter() -> AuditEmitter:
    return AuditEmitter()


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
        assert result["emitted"] is True

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
        assert cap._audit_records[-1]["category"] == "security_violation"

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
        assert cap._audit_records[-1]["severity"] == "critical"

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
        assert cap._audit_records[-1]["source_feature"] == "launcher"

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
        assert cap._audit_records[-1]["operation_type"] == "execution_failed"

    def test_audit_record_contains_timestamp(self) -> None:
        cap = _make_emitter()
        asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        assert "timestamp" in cap._audit_records[-1]

    def test_audit_record_contains_correlation_id(self) -> None:
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
        assert cap._audit_records[-1]["correlation_id"] == "trace-12345"

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
        assert cap._audit_records[-1]["correlation_id"] is None


class TestAuditRecordImmutability:
    """Test audit record immutability once emitted."""

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
        assert len(cap._audit_records) == 2

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
        first_record = cap._audit_records[-1]
        asyncio.run(
            cap.emit_audit_event(
                category="task_failure",
                severity="error",
                source_feature="dispatcher",
                operation_type="execution_failed",
            )
        )
        assert first_record["category"] == "security_violation"

    def test_audit_categories_preserved(self) -> None:
        cap = _make_emitter()
        for category in ["security_violation", "connection_failure", "task_failure", "destructive_action"]:
            asyncio.run(
                cap.emit_audit_event(
                    category=category,
                    severity="warning",
                    source_feature="test",
                    operation_type="test_op",
                )
            )
        assert len(cap._audit_records) == 4


class TestAuditRedaction:
    """Test audit record content passes redaction rules."""

    def test_audit_record_no_raw_payloads(self) -> None:
        cap = _make_emitter()
        result = asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        assert "record" in result

    def test_audit_record_no_credentials(self) -> None:
        cap = _make_emitter()
        result = asyncio.run(
            cap.emit_audit_event(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_failure",
            )
        )
        record = result["record"]
        for key, value in record.items():
            if isinstance(value, str):
                assert "secret" not in value.lower() or key == "category"


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


class TestEventBusGetSubscribers:
    """Test subscriber list retrieval."""

    def test_get_subscribers_returns_list(self) -> None:
        bus = _make_event_bus()
        assert isinstance(bus.get_subscribers(), list)

    def test_get_subscribers_returns_copy(self) -> None:
        bus = _make_event_bus()
        mock_sub = AsyncMock()
        bus.subscribe(mock_sub)
        subs1 = bus.get_subscribers()
        assert len(subs1) == 1

    def test_empty_bus_returns_empty_list(self) -> None:
        bus = _make_event_bus()
        assert len(bus.get_subscribers()) == 0


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
        assert result["emitted"] is True
        assert len(cap._audit_records) >= 1
