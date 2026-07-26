"""Diagnostics domain — contract protocols for observability."""

from .contract_audit_emission_protocol import AuditEmissionProtocol
from .contract_diagnostics_snapshot_protocol import DiagnosticsSnapshotProtocol
from .contract_health_composition_protocol import HealthCompositionProtocol
from .contract_logging_policy_protocol import LoggingPolicyProtocol
from .contract_metrics_collection_protocol import MetricsCollectionProtocol

__all__ = [
    "HealthCompositionProtocol",
    "MetricsCollectionProtocol",
    "AuditEmissionProtocol",
    "LoggingPolicyProtocol",
    "DiagnosticsSnapshotProtocol",
]
