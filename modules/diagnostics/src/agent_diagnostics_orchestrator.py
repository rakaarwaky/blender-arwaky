"""Diagnostics feature orchestrator implementing IDiagnosticsAggregate.

Coordinates health composition, metrics collection, audit emission,
structured logging policy, and snapshot provision through DiagnosticsCapability.

Orchestration only — delegates all business logic to capabilities
via protocol interfaces. Owns the bounded event ring buffer (T-09)
since diagnostics has 5 capabilities mapped 1:1 to FR-DIA-001..005.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from modules.diagnostics.src.capabilities_health_composition import DiagnosticsCapability

logger = logging.getLogger(__name__)


class DiagnosticsOrchestrator:
    """Orchestrates diagnostics operations across all subsystems.

    Provides a unified facade for health composition, metrics collection,
    audit emission, structured logging, and snapshot provision.
    Delegates to DiagnosticsCapability (FR-DIA-001..005).
    """

    def __init__(self, capability: DiagnosticsCapability) -> None:
        self._capability = capability

    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
    ) -> dict[str, Any]:
        """Compose system health from all subsystems.

        Aggregates launcher status, gateway connection state, config validity,
        job capacity, and asset provider availability into a single view.
        Implements FR-DIA-001.
        """
        return await self._capability.compose_health(
            launcher_status=launcher_status,
            gateway_status=gateway_status,
            config_valid=config_valid,
            job_capacity_available=job_capacity_available,
        )

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
        """Collect operational metrics from all features.

        Pulls counters, gauges, and latency summaries from launcher,
        gateway, dispatcher, job, security, and config features.
        Implements FR-DIA-002.
        """
        return await self._capability.collect_metrics_snapshot(
            pending_operations=pending_operations,
            reconnect_count=reconnect_count,
            execution_latency_ms=execution_latency_ms,
            command_latency_ms=command_latency_ms,
            failed_requests=failed_requests,
            security_violations=security_violations,
            tasks_created=tasks_created,
            tasks_failed=tasks_failed,
            tasks_completed=tasks_completed,
        )

    async def emit_audit_event(
        self,
        category: str,
        severity: str,
        source_feature: str,
        operation_type: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Emit an immutable audit record for security-relevant activity.

        Handles security violations, connection failures, task failures,
        and destructive actions with guaranteed fallback delivery.
        Implements FR-DIA-003.
        """
        return await self._capability.emit_audit_event(
            category=category,
            severity=severity,
            source_feature=source_feature,
            operation_type=operation_type,
            correlation_id=correlation_id,
        )

    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
    ) -> dict[str, Any]:
        """Write sanitized structured log entry.

        All features log through this policy; private per-feature log formats
        are not permitted. Redaction applied at ingestion.
        Implements FR-DIA-004.
        """
        return await self._capability.log_record(
            level=level,
            source_feature=source_feature,
            message=message,
            fields=fields,
            tracking_id=tracking_id,
        )

    async def get_snapshot(
        self,
        detail_level: str = "summary",
        section_filter: list[str] | None = None,
    ) -> dict[str, Any]:
        """Provide a point-in-time diagnostics snapshot.

        Combines composed health, metrics snapshot, recent audit summary,
        and configuration metadata into a consistent view.
        Implements FR-DIA-005.
        """
        return await self._capability.get_snapshot(
            detail_level=detail_level,
            section_filter=section_filter,
        )
