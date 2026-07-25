"""Object domain contract: set material protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import SetMaterialRequestVO
from .taxonomy_object_result_vo import MaterialResultVO


class SetMaterialProtocol(ABC):
    """Protocol interface for assigning or creating a material on an object."""

    @abstractmethod
    async def set_material(self, request: SetMaterialRequestVO) -> MaterialResultVO:
        """Assign or create a material for an object.

        FR-OBJ-004: Creates material if it doesn't exist; assigns to first slot
        or specified slot index. Validates object is a mesh type.
        """
        ...
