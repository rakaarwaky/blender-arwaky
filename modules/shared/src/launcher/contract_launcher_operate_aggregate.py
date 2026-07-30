"""Launcher domain contract: launcher operate aggregate (ABC).

The Agent implements this aggregate. Surface layers depend on it.
Facade for all 5 launcher operations: locate/register, launch, shutdown,
status, persist.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import FilePath

from .taxonomy_launcher_vo import (
    LaunchOutcomeVO,
    LaunchRequestVO,
    LoadOutcomeVO,
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
    """

    @abstractmethod
    def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """FR-LAU-001: Locate and register the Blender executable."""
        ...

    @abstractmethod
    def launch(self, request: LaunchRequestVO | None = None) -> LaunchOutcomeVO:
        """FR-LAU-002: Launch Blender and confirm readiness."""
        ...

    @abstractmethod
    def shutdown(self, request: ShutdownRequestVO | None = None) -> ShutdownOutcomeVO:
        """FR-LAU-003: Graceful-then-force shutdown."""
        ...

    @abstractmethod
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """FR-LAU-004: Verify true runtime status."""
        ...

    @abstractmethod
    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """FR-LAU-005: Persist runtime state (corruption-safe)."""
        ...

    @abstractmethod
    def load(self) -> LoadOutcomeVO:
        """FR-LAU-005: Load persisted state with corruption/parse warnings."""
        ...
