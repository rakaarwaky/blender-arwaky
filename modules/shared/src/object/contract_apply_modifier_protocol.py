"""Object domain contract: apply modifier protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import ApplyModifierVO


class ApplyModifierProtocol(ABC):
    """Protocol interface for adding, updating, removing, or applying a modifier."""

    @abstractmethod
    async def apply_modifier(self, request: ApplyModifierVO) -> ApplyModifierVO:
        """Add, update, remove, or apply a modifier on an object."""
        ...
