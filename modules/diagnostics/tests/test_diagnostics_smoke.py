"""Smoke test for the importable slice of the diagnostics module.

Exercises all 5 capabilities individually and the DiagnosticsOrchestrator.
"""

from __future__ import annotations

import asyncio

from modules.diagnostics.src.agent_diagnostics_orchestrator import (
    DiagnosticsOrchestrator,
)
from modules.diagnostics.src.capabilities_audit_emitter import AuditEmitter
from modules.diagnostics.src.capabilities_health_composer import HealthComposer
from modules.diagnostics.src.capabilities_logging_policy import LoggingPolicy
from modules.diagnostics.src.capabilities_metrics_collector import MetricsCollector
from modules.diagnostics.src.capabilities_snapshot_provisioner import SnapshotProvisioner
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    AuditEventRequestVO,
    HealthCompositionRequestVO,
    LogRecordRequestVO,
    MetricsSampleVO,
)


def test_health_composer_instantiates() -> None:
    cap = HealthComposer()
    assert isinstance(cap, HealthComposer)


def test_metrics_collector_instantiates() -> None:
    cap = MetricsCollector()
    assert isinstance(cap, MetricsCollector)


def test_audit_emitter_instantiates() -> None:
    cap = AuditEmitter()
    assert isinstance(cap, AuditEmitter)


def test_logging_policy_instantiates() -> None:
    cap = LoggingPolicy()
    assert isinstance(cap, LoggingPolicy)


def test_snapshot_provisioner_instantiates() -> None:
    cap = SnapshotProvisioner()
    assert isinstance(cap, SnapshotProvisioner)


def test_orchestrator_composes_all_capabilities() -> None:
    orch = DiagnosticsOrchestrator(
        health_composer=HealthComposer(),
        metrics_collector=MetricsCollector(),
        audit_emitter=AuditEmitter(),
        logging_policy=LoggingPolicy(),
        snapshot_provisioner=SnapshotProvisioner(),
    )
    assert isinstance(orch, DiagnosticsOrchestrator)


def test_compose_health_returns_overall_status() -> None:
    cap = HealthComposer()
    result = asyncio.run(
        cap.compose_health(
            request=HealthCompositionRequestVO(
                launcher_status="healthy",
                gateway_status="healthy",
                config_valid=True,
                job_capacity_available=True,
            )
        )
    )
    assert result.overall_status == "healthy"
    names = [s.name for s in result.subsystems]
    assert set(names) >= {"launcher", "gateway", "config", "job_capacity"}


def test_metrics_snapshot_collects_required_counters() -> None:
    cap = MetricsCollector()
    sample = MetricsSampleVO(
        pending_operations=2,
        reconnect_count=1,
        failed_requests=0,
        security_violations=0,
        tasks_created=5,
        tasks_failed=1,
        tasks_completed=4,
    )
    snap = asyncio.run(cap.collect_metrics_snapshot(sample=sample))
    assert snap.counters["tasks_created"] == 5
    assert snap.counters["tasks_failed"] == 1
    assert snap.counters["tasks_completed"] == 4


def test_emit_audit_event_appends_record() -> None:
    cap = AuditEmitter()
    out = asyncio.run(
        cap.emit_audit_event(
            request=AuditEventRequestVO(
                category="security_violation",
                severity="critical",
                source_feature="gateway",
                operation_type="connection_lost",
            )
        )
    )
    assert out.emission_confirmed is True
    assert cap._fallback_buffer[0].category == "security_violation"


def test_log_record_buffers_entry() -> None:
    cap = LoggingPolicy()
    out = asyncio.run(
        cap.log_record(
            request=LogRecordRequestVO(
                level="info",
                source_feature="cli",
                message="startup",
                fields={"x": 1},
            )
        )
    )
    assert out.logged is True
    assert cap._buffer[-1]["message"] == "startup"
