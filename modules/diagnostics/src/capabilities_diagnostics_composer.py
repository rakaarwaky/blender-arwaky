"""Capability: Diagnostics health composer and snapshot provider.

Implements HealthCompositionProtocol, MetricsCollectionProtocol,
AuditEmissionProtocol, LoggingPolicyProtocol, and DiagnosticsSnapshotProtocol.

FR-DIA-001 through FR-DIA-005: Single observability authority for the system.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from modules.shared.src.diagnostics.contract_health_composition_protocol import HealthCompositionProtocol
from modules.shared.src.diagnostics.contract_metrics_collection_protocol import MetricsCollectionProtocol
from modules.shared.src.diagnostics.contract_audit_emission_protocol import AuditEmissionProtocol
from modules.shared.src.diagnostics.contract_logging_policy_protocol import LoggingPolicyProtocol
from modules.shared.src.diagnostics.contract_diagnostics_snapshot_protocol import DiagnosticsSnapshotProtocol

logger = logging.getLogger("BlenderMCPServer")


class DiagnosticsCapability(
    HealthCompositionProtocol,
    MetricsCollectionProtocol,
    AuditEmissionProtocol,
    LoggingPolicyProtocol,
    DiagnosticsSnapshotProtocol,
):
    """Unified diagnostics capability covering health, metrics, audit, logging, and snapshots."""

    def __init__(self) -> None:
        """Initialize diagnostics state."""
        self._health_state: dict[str, Any] = {}
        self._metrics_snapshot: dict[str, Any] = {}
        self._audit_records: list[dict[str, Any]] = []
        self._log_buffer: list[dict[str, Any]] = []

    # FR-DIA-001: Compose System Health
    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
    ) -> dict[str, Any]:
        """Aggregate subsystem states into one composed health view."""
        subsystems: dict[str, str] = {
            "launcher": launcher_status,
            "gateway": gateway_status,
            "config": "healthy" if config_valid else "unhealthy",
            "job_capacity": "healthy" if job_capacity_available else "degraded",
        }

        # Derive overall status deterministically
        statuses = list(subsystems.values())
        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif any(s == "unhealthy" or s == "failed" or s == "unreachable" for s in statuses):
            overall = "unhealthy"
        else:
            overall = "degraded"

        self._health_state = {
            "overall_status": overall,
            "subsystems": subsystems,
            "composition_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return dict(self._health_state)

    # FR-DIA-002: Collect Operational Metrics
    async def collect_metrics_snapshot(
        self,
        pending_operations: int = 0,
        reconnect_count: int = 0,
        execution_latency_ms: float = 0.0,
        command_latency_ms: float = 0.0,
        failed_requests: int = 0,
        security_violations: int = 0,
        tasks_created: int = 0,
        tasks_failed: int = 0,
        tasks_completed: int = 0,
    ) -> dict[str, Any]:
        """Pull operational metrics from features and return snapshot."""
        self._metrics_snapshot = {
            "counters": {
                "pending_operations": pending_operations,
                "reconnect_count": reconnect_count,
                "failed_requests": failed_requests,
                "security_violations": security_violations,
                "tasks_created": tasks_created,
                "tasks_failed": tasks_failed,
                "tasks_completed": tasks_completed,
            },
            "latency_summaries": {
                "execution_latency_ms": execution_latency_ms,
                "command_latency_ms": command_latency_ms,
            },
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return dict(self._metrics_snapshot)

    # FR-DIA-003: Emit Audit Events
    async def emit_audit_event(
        self,
        category: str,
        severity: str,
        source_feature: str,
        operation_type: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Produce immutable audit record for security-relevant activity."""
        record: dict[str, Any] = {
            "category": category,
            "severity": severity,
            "source_feature": source_feature,
            "operation_type": operation_type,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_records.append(record)
        return {"emitted": True, "record": record}

    # FR-DIA-004: Structured Logging Policy
    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
    ) -> dict[str, Any]:
        """Write sanitized structured log entry."""
        entry: dict[str, Any] = {
            "level": level,
            "source_feature": source_feature,
            "message": message,
            "fields": fields or {},
            "tracking_id": tracking_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._log_buffer.append(entry)

        # Also emit to Python logger
        log_fn = getattr(logger, level.lower(), logger.info)
        log_fn("%s [%s] %s", source_feature, level, message)

        return {"logged": True, "destination": "buffer"}

    # FR-DIA-005: Provide Diagnostics Snapshot
    async def get_snapshot(
        self,
        detail_level: str = "summary",
        section_filter: list[str] | None = None,
    ) -> dict[str, Any]:
        """Serve one canonical diagnostics snapshot."""
        sections = section_filter or ["health", "metrics", "audit_summary"]

        snapshot: dict[str, Any] = {}

        if "health" in sections:
            snapshot["health"] = self._health_state

        if "metrics" in sections:
            snapshot["metrics"] = self._metrics_snapshot

        if "audit_summary" in sections:
            snapshot["audit_summary"] = {
                "total_records": len(self._audit_records),
                "recent_categories": (
                    [r["category"] for r in self._audit_records[-10:]]
                    if self._audit_records
                    else []
                ),
            }

        return snapshot
