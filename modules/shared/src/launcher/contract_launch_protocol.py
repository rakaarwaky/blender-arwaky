"""Launcher domain contract: launch protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-002: Launch Application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import LaunchResultVO


class LaunchProtocol(ABC):
    """Protocol interface for launching the Blender process with readiness wait."""

    @abstractmethod
    def launch(self, mode: str = "interface", readiness_timeout_seconds: float | None = None) -> LaunchResultVO:
        """Start Blender with the integration component active and confirm readiness."""
        ...
