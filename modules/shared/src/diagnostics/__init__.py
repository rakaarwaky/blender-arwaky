"""Diagnostics domain — contracts (protocols + aggregate) for cross-feature use."""

from .contract_audit_emission_protocol import AuditEmissionProtocol, AuditStateProviderProtocol
from .contract_diagnostics_aggregate import IDiagnosticsAggregate
from .contract_health_composition_protocol import HealthCompositionProtocol, HealthStateProviderProtocol
from .contract_logging_policy_protocol import LoggingPolicyProtocol
from .contract_metrics_collection_protocol import MetricsCollectionProtocol, MetricsStateProviderProtocol
from .contract_snapshot_provision_protocol import SnapshotProvisionProtocol
from .taxonomy_diagnostics_vo import (
    AuditEventRequestVO,
    AuditRecordVO,
    AuditSummaryVO,
    DiagnosticsConfigVO,
    DiagnosticsSnapshotVO,
    HealthCompositionRequestVO,
    HealthDetailsVO,
    LatencySummaryVO,
    LogRecordRequestVO,
    LogResultVO,
    MetricsSampleVO,
    MetricsSnapshotVO,
    SnapshotRequestVO,
    SubsystemHealthVO,
)

__all__ = [
    "AuditEventRequestVO",
    "AuditEmissionProtocol",
    "AuditRecordVO",
    "AuditStateProviderProtocol",
    "AuditSummaryVO",
    "DiagnosticsConfigVO",
    "DiagnosticsSnapshotVO",
    "HealthCompositionProtocol",
    "HealthCompositionRequestVO",
    "HealthDetailsVO",
    "HealthStateProviderProtocol",
    "IDiagnosticsAggregate",
    "LatencySummaryVO",
    "LogRecordRequestVO",
    "LogResultVO",
    "LoggingPolicyProtocol",
    "MetricsCollectionProtocol",
    "MetricsSampleVO",
    "MetricsSnapshotVO",
    "MetricsStateProviderProtocol",
    "SnapshotProvisionProtocol",
    "SnapshotRequestVO",
    "SubsystemHealthVO",
]
