"""Diagnostics domain — contracts (protocols + aggregate) for cross-feature use."""

from .contract_audit_emission_protocol import AuditEmissionProtocol
from .contract_diagnostics_aggregate import IDiagnosticsAggregate
from .contract_health_composition_protocol import HealthCompositionProtocol, HealthProbeResult, HealthSummaryVO
from .contract_logging_policy_protocol import LoggingPolicyProtocol, LogRecordVO
from .contract_metrics_collection_protocol import MetricsCollectionProtocol, MetricsSnapshotVO
from .contract_snapshot_provision_protocol import (
    DiagnosticsSnapshotProtocol,
    DiagnosticsSnapshotVO,
    SnapshotRequestVO,
)
from .taxonomy_diagnostics_vo import (
    AuditRecordVO,
    HealthStatusVO,
    LogResultVO,
    MetricSampleVO,
    ProbeOutcomeVO,
    ProbeTargetVO,
    SeverityLevel,
)

__all__ = [
    "AuditEmissionProtocol",
    "AuditRecordVO",
    "DiagnosticsSnapshotProtocol",
    "DiagnosticsSnapshotVO",
    "HealthCompositionProtocol",
    "HealthProbeResult",
    "HealthStatusVO",
    "HealthSummaryVO",
    "IDiagnosticsAggregate",
    "LogRecordVO",
    "LogResultVO",
    "LoggingPolicyProtocol",
    "MetricSampleVO",
    "MetricsCollectionProtocol",
    "MetricsSnapshotVO",
    "ProbeOutcomeVO",
    "ProbeTargetVO",
    "SeverityLevel",
    "SnapshotRequestVO",
]
