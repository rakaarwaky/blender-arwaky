"""Diagnostics domain contract: diagnostics aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for diagnostics operations: health, metrics, audit, logging, snapshot.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
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


class IDiagnosticsAggregate(ABC):
    """Aggregate facade for diagnostics operations.

    Agent implements this aggregate (DiagnosticsOrchestrator). Surface layers depend on it.
    Provides health composition, metrics collection, audit emission, logging, and snapshot retrieval.
    """

    @abstractmethod
    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO:
        ...

    @abstractmethod
    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO:
        ...

    @abstractmethod
    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        ...

    @abstractmethod
    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO:
        ...

    @abstractmethod
    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO:
        ...
