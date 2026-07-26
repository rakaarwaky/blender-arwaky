"""Launcher domain contract: launcher operate aggregate (ABC).

The Agent implements this aggregate. Surface layers depend on it.
Facade for all 5 launcher operations: locate/register, launch, shutdown,
status, persist.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchResultVO,
    PersistenceResultVO,
    RegistrationResultVO,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownResultVO,
)


class LauncherOperateAggregate(ABC):
    """Aggregate facade for all launcher operations.

    The Agent orchestrator implements this interface.
    """

    @abstractmethod
    def locate_and_register(self, config: LauncherConfigVO, override: str | None = None) -> RegistrationResultVO:
        """FR-LAU-001: Locate and register the Blender executable."""
        ...

    @abstractmethod
    def launch(self, mode: str = "interface", readiness_timeout_seconds: float | None = None) -> LaunchResultVO:
        """FR-LAU-002: Launch Blender and confirm readiness."""
        ...

    @abstractmethod
    def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownResultVO:
        """FR-LAU-003: Graceful-then-force shutdown."""
        ...

    @abstractmethod
    def check_status(self, depth: str = "lightweight") -> RuntimeStatusVO:
        """FR-LAU-004: Verify true runtime status."""
        ...

    @abstractmethod
    def persist(self, state: RuntimeStateVO) -> PersistenceResultVO:
        """FR-LAU-005: Persist runtime state (corruption-safe)."""
        ...
