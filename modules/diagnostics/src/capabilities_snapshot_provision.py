"""Capability: Diagnostics snapshot provisioner.

FR-DIA-005: Provide Diagnostics Snapshot
Serves one canonical point-in-time snapshot combining health, metrics,
recent audit summary, and config metadata.
Implements SnapshotProvisionProtocol.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from modules.shared.src.diagnostics.contract_snapshot_provision_protocol import (
    SnapshotProvisionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    AuditSummaryVO,
    DiagnosticsSnapshotVO,
    HealthDetailsVO,
    MetricsSnapshotVO,
)

logger = logging.getLogger(__name__)


class _HealthProvider(Protocol):
    """Protocol for accessing composed health state (DI boundary)."""

    async def get_health(self) -> HealthDetailsVO | None: ...


class _MetricsProvider(Protocol):
    """Protocol for accessing metrics snapshot (DI boundary)."""

    async def get_metrics(self) -> MetricsSnapshotVO | None: ...


class _AuditProvider(Protocol):
    """Protocol for accessing audit records (DI boundary)."""

    async def get_audit_summary(self) -> AuditSummaryVO | None: ...


class SnapshotProvisioner(SnapshotProvisionProtocol):
    """Provide point-in-time diagnostics snapshots.

    Composes health, metrics, audit summary into a consistent view.
    CLI/MCP consume this — never probe subsystems or compute health themselves.
    """

    def __init__(
        self,
        health_provider: _HealthProvider | None = None,
        metrics_provider: _MetricsProvider | None = None,
        audit_provider: _AuditProvider | None = None,
    ) -> None:
        self._health_provider = health_provider
        self._metrics_provider = metrics_provider
        self._audit_provider = audit_provider

    async def get_snapshot(
        self,
        detail_level: str = "summary",
        section_filter: list[str] | None = None,
    ) -> DiagnosticsSnapshotVO:
        """Serve one canonical point-in-time diagnostics snapshot."""
        sections = section_filter or ["health", "metrics", "audit_summary"]

        snapshot_parts: dict[str, Any] = {}

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

        # Check if any sections were populated (first-run indicator)
        first_run = len(snapshot_parts) == 0

        return DiagnosticsSnapshotVO(
            health=snapshot_parts.get("health"),
            metrics=snapshot_parts.get("metrics"),
            audit_summary=snapshot_parts.get("audit_summary"),
            detail_level=detail_level,
            staleness_indicators={},
            first_run_indicator=first_run,
        )

    def __repr__(self) -> str:
        return "SnapshotProvisioner()"
