"""Root: CLI feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
CLI module: Capabilities → Agent Orchestrator → (exposed as CliOrchestrator).

This file is the composition root for the CLI feature. It instantiates
concrete capability implementations, connects them to the agent orchestrator,
and provides the assembled orchestrator for dependency injection by callers.
"""

from __future__ import annotations

import logging

from .agent_orchestrator import CliOrchestrator
from .capabilities_cli_lifecycle import CliLifecycleManager

logger = logging.getLogger("BlenderMCPServer")


class CliContainer:
    """Dependency injection container for the CLI feature module.

    Wires the CLI lifecycle capability to the orchestrator. The lifecycle
    capability requires a blender_manager dependency, injected by the caller
    (the surface/launcher that owns the Blender process).
    """

    def __init__(self, blender_manager: object | None = None) -> None:
        self._blender_manager = blender_manager
        self._orchestrator: CliOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the CLI lifecycle capability to the orchestrator."""
        if self._wired:
            return

        logger.info("Wiring CLI feature module")

        lifecycle_cap = CliLifecycleManager(blender_manager=self._blender_manager)
        self._orchestrator = CliOrchestrator(lifecycle=lifecycle_cap)

        self._wired = True
        logger.info("CLI feature module wired successfully")

    @property
    def agent(self) -> CliOrchestrator:
        """Return the assembled CLI orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("CliContainer not wired — call wire() first")
        return self._orchestrator


def create_cli_feature(blender_manager: object | None = None) -> CliOrchestrator:
    """Factory function to create and wire the CLI feature module."""
    container = CliContainer(blender_manager=blender_manager)
    container.wire()
    return container.agent