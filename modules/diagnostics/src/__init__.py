"""Diagnostics feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/gateway/)     → VOs, Errors, Events, Constants
  - Contract (4 protocols)              → HealthComposition, MetricsCollection, AuditEmission, LoggingPolicy
  - Capabilities (4 files)              → HealthComposer, MetricsCollector, AuditEmitter, LoggingPolicy + InMemoryEventBus
  - Agent                               → DiagnosticsOrchestrator (composes 4 capabilities)
  - Root                                → DiagnosticsContainer (DI wiring)
"""

from .agent_diagnostics_orchestrator import DiagnosticsOrchestrator
from .capabilities_audit_emission import AuditEmitter, InMemoryEventBus
from .capabilities_health_composition import HealthComposer
from .capabilities_logging_policy import LoggingPolicy
from .capabilities_metrics_collection import MetricsCollector
from .root_diagnostics_container import DiagnosticsContainer, create_diagnostics_feature

__all__ = [
    "HealthComposer",
    "MetricsCollector",
    "AuditEmitter",
    "LoggingPolicy",
    "InMemoryEventBus",
    "DiagnosticsOrchestrator",
    "DiagnosticsContainer",
    "create_diagnostics_feature",
]
