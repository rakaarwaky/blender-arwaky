"""Diagnostics feature orchestrator implementing IDiagnosticsAggregate.

Coordinates health composition, metrics collection, audit emission,
structured logging policy, and snapshot provision through 5 separate
capabilities (FR-DIA-001..005).

Orchestration only — delegates all business logic to capabilities
via protocol interfaces.
"""

from __future__ import annotations

from modules.shared.src.diagnostics.contract_diagnostics_aggregate import (
    IDiagnosticsAggregate,
)
from modules.shared.src.diagnostics.contract_health_composition_protocol import (
    HealthCompositionProtocol,
)
from modules.shared.src.diagnostics.contract_logging_policy_protocol import (
    LoggingPolicyProtocol,
)
from modules.shared.src.diagnostics.contract_metrics_collection_protocol import (
    MetricsCollectionProtocol,
)
from modules.shared.src.diagnostics.contract_snapshot_provision_protocol import (
    SnapshotProvisionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    AuditEventRequestVO,
    AuditRecordVO,
    DiagnosticsSnapshotVO,
    HealthCompositionRequestVO,
    HealthDetailsVO,
    LogRecordRequestVO,
    LogResultVO,
    MetricsSampleVO,
    MetricsSnapshotVO,
    SnapshotRequestVO,
)


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
        audit_emitter: "AuditEmissionProtocol",
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
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO:
        """Compose system health from all subsystems.

        FR-DIA-001.
        """
        return await self._health_composer.compose_health(request)

    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO:
        """Collect operational metrics from all features.

        FR-DIA-002.
        """
        return await self._metrics_collector.collect_metrics_snapshot(sample)

    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        """Emit an immutable audit record for security-relevant activity.

        FR-DIA-003.
        """
        return await self._audit_emitter.emit_audit_event(request)

    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO:
        """Write sanitized structured log entry.

        FR-DIA-004.
        """
        return await self._logging_policy.log_record(request)

    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO:
        """Provide a point-in-time diagnostics snapshot.

        FR-DIA-005.
        """
        return await self._snapshot_provisioner.get_snapshot(request)

    def __repr__(self) -> str:
        return "DiagnosticsOrchestrator()"
