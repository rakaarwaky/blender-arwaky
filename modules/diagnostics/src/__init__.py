"""Diagnostics feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/diagnostics/) → VOs, Errors, Events, Constants
  - Contract (shared/src/diagnostics/)   → 2 individual protocols + Aggregate ABC
  - Capabilities (2 executors)              → One per FR-DIA operation
  - Agent                                   → DiagnosticsOrchestrator (Aggregate facade)
  - Root                                    → DiagnosticsContainer (DI wiring)
"""

from .capabilities_audit_emission import InMemoryEventBus
from .capabilities_health_composition import DiagnosticsCapability
from .root_diagnostics_container import DiagnosticsContainer, create_diagnostics_feature

__all__ = [
    "InMemoryEventBus",
    "DiagnosticsCapability",
    "DiagnosticsContainer",
    "create_diagnostics_feature",
]
