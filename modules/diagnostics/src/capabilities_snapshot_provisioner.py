"""Capability: Diagnostics snapshot provisioner.

FR-DIA-005: Provide Diagnostics Snapshot
Serves one canonical point-in-time snapshot combining health, metrics,
recent audit summary, and config metadata.
Implements SnapshotProvisionProtocol.
"""

from __future__ import annotations

import logging

from modules.shared.src.diagnostics.contract_audit_state_provider_protocol import (
    AuditStateProviderProtocol,
)
from modules.shared.src.diagnostics.contract_health_state_provider_protocol import (
    HealthStateProviderProtocol,
)
from modules.shared.src.diagnostics.contract_metrics_state_provider_protocol import (
    MetricsStateProviderProtocol,
)
from modules.shared.src.diagnostics.contract_snapshot_provision_protocol import (
    SnapshotProvisionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    DiagnosticsSnapshotVO,
    SnapshotRequestVO,
)

logger = logging.getLogger(__name__)


class SnapshotProvisioner(SnapshotProvisionProtocol):
    """Provide point-in-time diagnostics snapshots.

    Composes health, metrics, audit summary into a consistent view.
    CLI/MCP consume this — never probe subsystems or compute health themselves.
    """

    def __init__(
        self,
        health_provider: HealthStateProviderProtocol | None = None,
        metrics_provider: MetricsStateProviderProtocol | None = None,
        audit_provider: AuditStateProviderProtocol | None = None,
    ) -> None:
        self._health_provider = health_provider
        self._metrics_provider = metrics_provider
        self._audit_provider = audit_provider

    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO:
        """Serve one canonical point-in-time diagnostics snapshot."""
        sections = set(request.section_filter or ("health", "metrics", "audit_summary"))
        snapshot_parts: dict = {}

        if "health" in sections and self._health_provider:
            health = await self._health_provider.get_health()
            if health is not None:
                snapshot_parts["health"] = health

        if "metrics" in sections and self._metrics_provider:
            metrics = await self._metrics_provider.get_metrics()
            if metrics is not None:
                snapshot_parts["metrics"] = metrics

        if "audit_summary" in sections and self._audit_provider:
            audit = await self._audit_provider.get_audit_summary()
            if audit is not None:
                snapshot_parts["audit_summary"] = audit

        first_run = len(snapshot_parts) == 0

        return DiagnosticsSnapshotVO(
            health=snapshot_parts.get("health"),
            metrics=snapshot_parts.get("metrics"),
            audit_summary=snapshot_parts.get("audit_summary"),
            detail_level=request.detail_level,
            staleness_indicators={},
            first_run_indicator=first_run,
        )

    def __repr__(self) -> str:
        return "SnapshotProvisioner()"
