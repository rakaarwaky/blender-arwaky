"""Diagnostics feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/diagnostics/) → VOs, Errors, Events, Constants
  - Contract (shared/src/diagnostics/)   → 6 individual protocols + Aggregate ABC
  - Capabilities (1 unified capability)   → DiagnosticsCapability (FR-DIA-001..005)
  - Agent                                   → DiagnosticsOrchestrator (Aggregate facade)
  - Root                                    → DiagnosticsContainer (DI wiring)
"""

from .agent_diagnostics_orchestrator import DiagnosticsOrchestrator
from .capabilities_audit_emission import InMemoryEventBus
from .capabilities_health_composition import DiagnosticsCapability
from .root_diagnostics_container import DiagnosticsContainer, create_diagnostics_feature

__all__ = [
    "DiagnosticsCapability",
    "DiagnosticsContainer",
    "DiagnosticsOrchestrator",
    "InMemoryEventBus",
    "create_diagnostics_feature",
]
