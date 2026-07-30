"""Launcher domain contract: shutdown protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-003: Shut Down Application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import ShutdownOutcomeVO, ShutdownRequestVO


class ShutdownProtocol(ABC):
    """Protocol interface for graceful-then-force shutdown of the Blender process.

    Accepts a ShutdownRequestVO with explicit force/escalation semantics.
    """

    @abstractmethod
    def shutdown(self, request: ShutdownRequestVO | None = None) -> ShutdownOutcomeVO:
        """Stop Blender gracefully, escalating to force termination when allowed.

        Accepts a ShutdownRequestVO with force_requested and escalation_confirmed.
        None defaults to configured values.
        """
        ...
