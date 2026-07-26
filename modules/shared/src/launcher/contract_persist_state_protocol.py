"""Launcher domain contract: persist state protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-LAU-005: Persist Runtime State.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import PersistenceResultVO, RuntimeStateVO


class PersistStateProtocol(ABC):
    """Protocol interface for corruption-safe runtime state persistence."""

    @abstractmethod
    def persist(self, state: RuntimeStateVO) -> PersistenceResultVO:
        """Atomically persist runtime state; corrupt reads fall back to empty."""
        ...

    @abstractmethod
    def load(self) -> RuntimeStateVO | None:
        """Load persisted state, returning None on missing/corrupt content."""
        ...
