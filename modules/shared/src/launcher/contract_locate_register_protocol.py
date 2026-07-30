"""Launcher domain contract: locate & register protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-001: Locate and Register Application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import FilePath

from .taxonomy_launcher_vo import RegistrationOutcomeVO


class LocateRegisterProtocol(ABC):
    """Protocol interface for discovering and registering the Blender executable."""

    @abstractmethod
    def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """Discover, validate, and register a Blender executable per discovery order."""
        ...
