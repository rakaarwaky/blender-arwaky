"""Root: Diagnostics feature composition container.

Wires 5 capabilities (FR-DIA-001..005) + InMemoryEventBus and exposes
the DiagnosticsOrchestrator as the feature facade.

This file is the composition root for the diagnostics feature.
"""

from __future__ import annotations

import logging

from modules.diagnostics.src.agent_diagnostics_orchestrator import DiagnosticsOrchestrator
from modules.diagnostics.src.capabilities_audit_emission import (
    AuditEmitter,
    InMemoryEventBus,
)
from modules.diagnostics.src.capabilities_health_composition import HealthComposer
from modules.diagnostics.src.capabilities_logging_policy import LoggingPolicy
from modules.diagnostics.src.capabilities_metrics_collection import MetricsCollector
from modules.diagnostics.src.capabilities_snapshot_provision import SnapshotProvisioner

logger = logging.getLogger("BlenderMCPServer")


class DiagnosticsContainer:
    """Dependency injection container for the diagnostics feature module.

    Wires HealthComposer, MetricsCollector, AuditEmitter, LoggingPolicy,
    SnapshotProvisioner, and InMemoryEventBus into the DiagnosticsOrchestrator.
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
        snapshot_provisioner = SnapshotProvisioner(
            health_provider=health_composer,
            metrics_provider=metrics_collector,
            audit_provider=None,  # Will be wired by caller if needed
        )

        self._orchestrator = DiagnosticsOrchestrator(
            health_composer=health_composer,
            metrics_collector=metrics_collector,
            audit_emitter=audit_emitter,
            logging_policy=logging_policy,
            snapshot_provisioner=snapshot_provisioner,
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
