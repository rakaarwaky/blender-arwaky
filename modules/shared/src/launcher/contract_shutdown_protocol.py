"""Launcher domain contract: shutdown protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-003: Shut Down Application.

P0: Updated to accept ShutdownRequestVO instead of primitive parameters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import ShutdownOutcomeVO, ShutdownRequestVO


class ShutdownProtocol(ABC):
    """Protocol interface for graceful-then-force shutdown of the Blender process."""

    @abstractmethod
    def shutdown(self, request: ShutdownRequestVO) -> ShutdownOutcomeVO:
        """Stop Blender gracefully, escalating to force termination when allowed.

        P0: Accepts ShutdownRequestVO instead of primitive parameters.
        """
        ...
