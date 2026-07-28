"""Root: Diagnostics feature composition container.

The diagnostics feature has no separate agent layer — DiagnosticsCapability
is the unified implementation of the five diagnostics protocols
(HealthComposition, MetricsCollection, AuditEmission, LoggingPolicy,
DiagnosticsSnapshot). This container wires DiagnosticsCapability together with
the InMemoryEventBus and exposes the capability as the diagnostics facade.

This file is the composition root for the diagnostics feature.
"""

from __future__ import annotations

import logging

from .capabilities_health_composition import DiagnosticsCapability
from .capabilities_audit_emission import InMemoryEventBus

logger = logging.getLogger("BlenderMCPServer")


class DiagnosticsContainer:
    """Dependency injection container for the diagnostics feature module.

    Wires the unified diagnostics capability with the event bus.
    """

    def __init__(self) -> None:
        self._capability: DiagnosticsCapability | None = None
        self._event_bus: InMemoryEventBus | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the diagnostics capability with the event bus."""
        if self._wired:
            return

        logger.info("Wiring diagnostics feature module")

        self._event_bus = InMemoryEventBus()
        self._capability = DiagnosticsCapability()

        self._wired = True
        logger.info("Diagnostics feature module wired successfully")

    @property
    def agent(self) -> DiagnosticsCapability:
        """Return the assembled diagnostics capability facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._capability is None:
            raise RuntimeError("DiagnosticsContainer not wired — call wire() first")
        return self._capability


def create_diagnostics_feature() -> DiagnosticsCapability:
    """Factory function to create and wire the diagnostics feature module."""
    container = DiagnosticsContainer()
    container.wire()
    return container.agent
