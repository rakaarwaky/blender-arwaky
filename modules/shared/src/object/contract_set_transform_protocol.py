"""Object domain contract: set transform protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import SetObjectTransformVO


class SetObjectTransformProtocol(ABC):
    """Protocol interface for modifying an object's transform.

    FR-OBJ-003: Set Transform
    """

    @abstractmethod
    async def set_object_transform(self, request: SetObjectTransformVO) -> SetObjectTransformVO:
        """Modify location, rotation, or scale of an existing object."""
        ...
