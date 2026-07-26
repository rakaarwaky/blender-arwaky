"""Launcher domain contract: locate & register protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-001: Locate and Register Application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import LauncherConfigVO, RegistrationResultVO


class LocateRegisterProtocol(ABC):
    """Protocol interface for discovering and registering the Blender executable."""

    @abstractmethod
    def locate_and_register(self, config: LauncherConfigVO, override: str | None = None) -> RegistrationResultVO:
        """Discover, validate, and register a Blender executable per discovery order."""
        ...
