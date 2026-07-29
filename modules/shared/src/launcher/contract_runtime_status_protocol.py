"""Launcher domain contract: runtime status protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-004: Check Runtime Status.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import ProbeDepth, RuntimeStatusVO


class RuntimeStatusProtocol(ABC):
    """Protocol interface for verifying true process liveness and staleness."""

    @abstractmethod
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """Verify actual liveness (not persisted state) and classify runtime state."""
        ...
