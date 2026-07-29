"""Root: Diagnostics feature composition container.

Wires 4 capabilities (FR-DIA-001..004) + InMemoryEventBus and exposes
the DiagnosticsOrchestrator as the feature facade.

This file is the composition root for the diagnostics feature.
"""

from __future__ import annotations

import logging

from .capabilities_audit_emission import AuditEmitter, InMemoryEventBus
from .capabilities_health_composition import HealthComposer
from .capabilities_logging_policy import LoggingPolicy
from .capabilities_metrics_collection import MetricsCollector
from .agent_diagnostics_orchestrator import DiagnosticsOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class DiagnosticsContainer:
    """Dependency injection container for the diagnostics feature module.

    Wires HealthComposer, MetricsCollector, AuditEmitter, LoggingPolicy,
    and InMemoryEventBus into the DiagnosticsOrchestrator.
    """

    def __init__(self) -> None:
        self._orchestrator: DiagnosticsOrchestrator | None = None
        self._event_bus: InMemoryEventBus | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the diagnostics feature module."""
        if self._wired:
            return

        logger.info("Wiring diagnostics feature module")

        self._event_bus = InMemoryEventBus()
        health_composer = HealthComposer()
        metrics_collector = MetricsCollector()
        audit_emitter = AuditEmitter()
        logging_policy = LoggingPolicy()

        self._orchestrator = DiagnosticsOrchestrator(
            health_composer=health_composer,
            metrics_collector=metrics_collector,
            audit_emitter=audit_emitter,
            logging_policy=logging_policy,
        )

        self._wired = True
        logger.info("Diagnostics feature module wired successfully")

    @property
    def agent(self) -> DiagnosticsOrchestrator:
        """Return the assembled diagnostics orchestrator.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("DiagnosticsContainer not wired — call wire() first")
        return self._orchestrator

    @property
    def event_bus(self) -> InMemoryEventBus:
        """Return the InMemoryEventBus instance."""
        if not self._wired or self._event_bus is None:
            raise RuntimeError("DiagnosticsContainer not wired — call wire() first")
        return self._event_bus


def create_diagnostics_feature() -> DiagnosticsOrchestrator:
    """Factory function to create and wire the diagnostics feature module."""
    container = DiagnosticsContainer()
    container.wire()
    return container.agent
