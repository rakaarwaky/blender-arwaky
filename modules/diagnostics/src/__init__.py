"""Diagnostics feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/diagnostics/) → VOs: HealthDetailsVO, MetricsSnapshotVO,
    AuditRecordVO, LogResultVO, DiagnosticsSnapshotVO, request/config VOs
  - Contract (shared/src/diagnostics/) → protocols + aggregate
  - Capabilities (5 files)          → HealthComposer, MetricsCollector,
    AuditEmitter, LoggingPolicy, SnapshotProvisioner
  - Agent                           → DiagnosticsOrchestrator
  - Root                            → DiagnosticsContainer (DI wiring)
"""

from .agent_diagnostics_orchestrator import DiagnosticsOrchestrator
from .capabilities_audit_emitter import AuditEmitter
from .capabilities_health_composer import HealthComposer
from .capabilities_logging_policy import LoggingPolicy
from .capabilities_metrics_collector import MetricsCollector
from .capabilities_snapshot_provisioner import SnapshotProvisioner
from .root_diagnostics_container import DiagnosticsContainer, create_diagnostics_feature

__all__ = [
    "HealthComposer",
    "MetricsCollector",
    "AuditEmitter",
    "LoggingPolicy",
    "SnapshotProvisioner",
    "DiagnosticsOrchestrator",
    "DiagnosticsContainer",
    "create_diagnostics_feature",
]
