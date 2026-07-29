"""Diagnostics module — health, metrics, audit, structured logging."""

from modules.diagnostics.src.agent_diagnostics_orchestrator import (
    DiagnosticsOrchestrator,
)
from modules.diagnostics.src.capabilities_audit_emission import (
    AuditEmitter,
    InMemoryEventBus,
)
from modules.diagnostics.src.capabilities_health_composition import HealthComposer
from modules.diagnostics.src.capabilities_logging_policy import LoggingPolicy
from modules.diagnostics.src.capabilities_metrics_collection import MetricsCollector
from modules.diagnostics.src.root_diagnostics_container import (
    DiagnosticsContainer,
    create_diagnostics_feature,
)

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
