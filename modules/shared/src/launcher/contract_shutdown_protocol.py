"""Launcher domain contract: shutdown protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-003: Shut Down Application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import ShutdownResultVO


class ShutdownProtocol(ABC):
    """Protocol interface for graceful-then-force shutdown of the Blender process."""

    @abstractmethod
    def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownResultVO:
        """Stop Blender gracefully, escalating to force termination when allowed."""
        ...