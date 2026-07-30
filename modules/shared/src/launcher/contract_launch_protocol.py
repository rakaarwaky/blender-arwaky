"""Launcher domain contract: launch protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-002: Launch Application.

P0: Updated to accept LaunchRequestVO instead of primitive parameters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import LaunchOutcomeVO, LaunchRequestVO


class LaunchProtocol(ABC):
    """Protocol interface for launching the Blender process with readiness wait."""

    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """Start Blender with the integration component active and confirm readiness.

        P0: Accepts LaunchRequestVO instead of primitive parameters.
        """
        ...
