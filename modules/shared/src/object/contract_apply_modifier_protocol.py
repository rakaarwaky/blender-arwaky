"""Object domain contract: apply modifier protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import ApplyModifierRequestVO
from .taxonomy_object_result_vo import ModifierResultVO


class ApplyModifierProtocol(ABC):
    """Protocol interface for adding, updating, removing, or applying a modifier."""

    @abstractmethod
    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ModifierResultVO:
        """Add, update, remove, or apply a modifier on an object.

        FR-OBJ-005: Maps human-readable modifier name to Blender enum,
        creates the modifier, then applies it destructively via operator.
        """
        ...
