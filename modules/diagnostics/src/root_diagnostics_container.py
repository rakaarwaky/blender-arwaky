"""Root: Diagnostics feature composition container.

Wires 5 capabilities (FR-DIA-001..005) and exposes
the DiagnosticsOrchestrator as the feature facade.

This file is the composition root for the diagnostics feature.
"""

from __future__ import annotations

import logging

from modules.diagnostics.src.agent_diagnostics_orchestrator import DiagnosticsOrchestrator
from modules.diagnostics.src.capabilities_audit_emitter import AuditEmitter
from modules.diagnostics.src.capabilities_health_composer import HealthComposer
from modules.diagnostics.src.capabilities_logging_policy import LoggingPolicy
from modules.diagnostics.src.capabilities_metrics_collector import MetricsCollector
from modules.diagnostics.src.capabilities_snapshot_provisioner import SnapshotProvisioner
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import DiagnosticsConfigVO

logger = logging.getLogger("BlenderMCPServer")


class DiagnosticsContainer:
    """Dependency injection container for the diagnostics feature module.

    Wires HealthComposer, MetricsCollector, AuditEmitter, LoggingPolicy,
    SnapshotProvisioner into the DiagnosticsOrchestrator.
    """

    def __init__(self, config: DiagnosticsConfigVO | None = None) -> None:
        self._config = config or DiagnosticsConfigVO()
        self._orchestrator: DiagnosticsOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the diagnostics feature module."""
        if self._wired:
            return

        logger.info("Wiring diagnostics feature module")

        health_composer = HealthComposer(
            probe_timeout_seconds=self._config.health_probe_timeout_seconds,
            freshness_tolerance_seconds=self._config.freshness_tolerance_seconds,
        )
        metrics_collector = MetricsCollector()
        audit_emitter = AuditEmitter(max_buffer_size=self._config.audit_max_buffer_size)
        logging_policy = LoggingPolicy(max_buffer_size=self._config.logging_max_buffer_size)
        snapshot_provisioner = SnapshotProvisioner(
            health_provider=health_composer,
            metrics_provider=metrics_collector,
            audit_provider=None,
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


def create_diagnostics_feature(
    config: DiagnosticsConfigVO | None = None,
) -> DiagnosticsOrchestrator:
    """Factory function to create and wire the diagnostics feature module."""
    container = DiagnosticsContainer(config=config)
    container.wire()
    return container.agent
