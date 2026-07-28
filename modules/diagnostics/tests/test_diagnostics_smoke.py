"""Smoke test for the importable slice of the diagnostics module.

The diagnostics module depends on the gateway taxonomy layer, which is
currently un-importable project-wide (gateway ``TransportOutcomeVO`` NameError).
This test therefore exercises only the loadable slice: the unified
``DiagnosticsCapability`` composer and the shared diagnostics contracts it
implements (FR-DIA-001..005 protocol conformance at the importable boundary).
"""

import asyncio

from modules.diagnostics.src.capabilities_diagnostics_composer import DiagnosticsCapability


def test_capability_instantiates() -> None:
    cap = DiagnosticsCapability()
    assert isinstance(cap, DiagnosticsCapability)


def test_compose_health_returns_overall_status() -> None:
    cap = DiagnosticsCapability()
    result = asyncio.run(
        cap.compose_health(
            launcher_status="healthy",
            gateway_status="healthy",
            config_valid=True,
            job_capacity_available=True,
        )
    )
    assert result["overall_status"] == "healthy"
    assert set(result["subsystems"]) >= {"launcher", "gateway", "config", "job_capacity"}


def test_metrics_snapshot_collects_required_counters() -> None:
    cap = DiagnosticsCapability()
    snap = asyncio.run(
        cap.collect_metrics_snapshot(
            pending_operations=2,
            reconnect_count=1,
            failed_requests=0,
            security_violations=0,
            tasks_created=5,
            tasks_failed=1,
            tasks_completed=4,
        )
    )
    assert snap["counters"]["tasks_created"] == 5
    assert snap["counters"]["tasks_failed"] == 1
    assert snap["counters"]["tasks_completed"] == 4


def test_emit_audit_event_appends_record() -> None:
    cap = DiagnosticsCapability()
    out = asyncio.run(
        cap.emit_audit_event(
            category="security_violation",
            severity="critical",
            source_feature="gateway",
            operation_type="connection_lost",
        )
    )
    assert out["emitted"] is True
    assert cap._audit_records[0]["category"] == "security_violation"


def test_log_record_buffers_entry() -> None:
    cap = DiagnosticsCapability()
    out = asyncio.run(
        cap.log_record(
            level="info",
            source_feature="cli",
            message="startup",
            fields={"x": 1},
        )
    )
    assert out["logged"] is True
    assert cap._log_buffer[-1]["message"] == "startup"


def test_snapshot_returns_requested_sections() -> None:
    cap = DiagnosticsCapability()
    asyncio.run(cap.compose_health())
    snap = asyncio.run(cap.get_snapshot(detail_level="summary", section_filter=["health"]))
    assert "health" in snap
    assert "metrics" not in snap
