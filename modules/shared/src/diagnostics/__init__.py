"""Diagnostics domain — contracts (protocols + aggregate) for cross-feature use."""

from .contract_audit_emission_protocol import AuditEmissionProtocol
from .contract_diagnostics_aggregate import IDiagnosticsAggregate
from .contract_health_composition_protocol import HealthCompositionProtocol
from .contract_logging_policy_protocol import LoggingPolicyProtocol
from .contract_metrics_collection_protocol import MetricsCollectionProtocol, MetricsSnapshotVO
from .contract_snapshot_provision_protocol import (
    DiagnosticsSnapshotProtocol,
    DiagnosticsSnapshotVO,
)
from .taxonomy_diagnostics_vo import (
    AuditRecordVO,
    AuditSummaryVO,
    DiagnosticsSnapshotVO,
    HealthDetailsVO,
    LatencySummaryVO,
    LogResultVO,
    MetricsSnapshotVO,
    SubsystemHealthVO,
)

__all__ = [
    "AuditEmissionProtocol",
    "AuditRecordVO",
    "AuditSummaryVO",
    "DiagnosticsSnapshotProtocol",
    "DiagnosticsSnapshotVO",
    "HealthCompositionProtocol",
    "HealthDetailsVO",
    "IDiagnosticsAggregate",
    "LatencySummaryVO",
    "LogResultVO",
    "LoggingPolicyProtocol",
    "MetricsCollectionProtocol",
    "MetricsSnapshotVO",
    "SubsystemHealthVO",
]
