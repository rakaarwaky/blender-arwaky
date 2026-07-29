"""Diagnostics feature orchestrator implementing IDiagnosticsAggregate.

Coordinates health composition, metrics collection, audit emission,
structured logging policy, and snapshot provision through 5 separate
capabilities (FR-DIA-001..005).

Orchestration only — delegates all business logic to capabilities
via protocol interfaces.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.diagnostics.contract_audit_emission_protocol import AuditEmissionProtocol
from modules.shared.src.diagnostics.contract_diagnostics_aggregate import IDiagnosticsAggregate
from modules.shared.src.diagnostics.contract_health_composition_protocol import (
    HealthCompositionProtocol,
)
from modules.shared.src.diagnostics.contract_logging_policy_protocol import LoggingPolicyProtocol
from modules.shared.src.diagnostics.contract_metrics_collection_protocol import (
    MetricsCollectionProtocol,
)
from modules.shared.src.diagnostics.contract_snapshot_provision_protocol import (
    SnapshotProvisionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    AuditRecordVO,
    DiagnosticsSnapshotVO,
    HealthDetailsVO,
    LogResultVO,
    MetricsSnapshotVO,
)

logger = logging.getLogger(__name__)


class DiagnosticsOrchestrator(IDiagnosticsAggregate):
    """Orchestrates diagnostics operations across all subsystems.

    Provides a unified facade for health composition, metrics collection,
    audit emission, structured logging, and snapshot provision.
    Delegates to 5 capabilities (FR-DIA-001..005) via contract protocols.
    """

    def __init__(
        self,
        health_composer: HealthCompositionProtocol,
        metrics_collector: MetricsCollectionProtocol,
        audit_emitter: AuditEmissionProtocol,
        logging_policy: LoggingPolicyProtocol,
        snapshot_provisioner: SnapshotProvisionProtocol,
    ) -> None:
        self._health_composer = health_composer
        self._metrics_collector = metrics_collector
        self._audit_emitter = audit_emitter
        self._logging_policy = logging_policy
        self._snapshot_provisioner = snapshot_provisioner

    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
    ) -> HealthDetailsVO:
        """Compose system health from all subsystems.

        Aggregates launcher status, gateway connection state, config validity,
        job capacity, and asset provider availability into a single view.
        Implements FR-DIA-001.
        """
        return await self._health_composer.compose_health(
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
    ) -> MetricsSnapshotVO:
        """Collect operational metrics from all features.

        Pulls counters, gauges, and latency summaries from launcher,
        gateway, dispatcher, job, security, and config features.
        Implements FR-DIA-002.
        """
        return await self._metrics_collector.collect_metrics_snapshot(
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
        target_metadata: dict | None = None,
        correlation_id: str | None = None,
    ) -> AuditRecordVO:
        """Emit an immutable audit record for security-relevant activity.

        Handles security violations, connection failures, task failures,
        and destructive actions with guaranteed fallback delivery.
        Implements FR-DIA-003.
        """
        return await self._audit_emitter.emit_audit_event(
            category=category,
            severity=severity,
            source_feature=source_feature,
            operation_type=operation_type,
            target_metadata=target_metadata,
            correlation_id=correlation_id,
        )

    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
    ) -> LogResultVO:
        """Write sanitized structured log entry.

        All features log through this policy; private per-feature log formats
        are not permitted. Redaction applied at ingestion.
        Implements FR-DIA-004.
        """
        return await self._logging_policy.log_record(
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
    ) -> DiagnosticsSnapshotVO:
        """Provide a point-in-time diagnostics snapshot.

        Delegates to SnapshotProvisioner capability (FR-DIA-005).
        Composes health, metrics, audit summary into a consistent view.
        """
        return await self._snapshot_provisioner.get_snapshot(
            detail_level=detail_level,
            section_filter=section_filter,
        )

    def __repr__(self) -> str:
        return "DiagnosticsOrchestrator()"
