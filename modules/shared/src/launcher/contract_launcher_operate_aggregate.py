"""Launcher domain contract: launcher operate aggregate (ABC).

The Agent implements this aggregate. Surface layers depend on it.
Facade for all 5 launcher operations: locate/register, launch, shutdown,
status, persist.

P0: Updated locate_and_register() to accept only optional override;
    config is injected internally by the implementation.
P0: Updated launch() and shutdown() signatures to match updated protocols.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import FilePath

from .taxonomy_launcher_vo import (
    LaunchOutcomeVO,
    LaunchRequestVO,
    PersistenceOutcomeVO,
    ProbeDepth,
    RegistrationOutcomeVO,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownOutcomeVO,
    ShutdownRequestVO,
)


class ILauncherOperateAggregate(ABC):
    """Aggregate facade for all launcher operations.

    The Agent orchestrator implements this interface.

    P0: locate_and_register() accepts only optional override — config is
        injected internally (config authority resolution).
    P0: launch() and shutdown() match updated protocol signatures.
    """

    @abstractmethod
    def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """FR-LAU-001: Locate and register the Blender executable.

        P0: Config is injected internally; caller passes only optional override.
        """
        ...

    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """FR-LAU-002: Launch Blender and confirm readiness.

        P0: Accepts LaunchRequestVO instead of primitive parameters.
        """
        ...

    @abstractmethod
    def shutdown(self, request: ShutdownRequestVO) -> ShutdownOutcomeVO:
        """FR-LAU-003: Graceful-then-force shutdown.

        P0: Accepts ShutdownRequestVO instead of primitive parameters.
        """
        ...

    @abstractmethod
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """FR-LAU-004: Verify true runtime status."""
        ...

    @abstractmethod
    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """FR-LAU-005: Persist runtime state (corruption-safe)."""
        ...
