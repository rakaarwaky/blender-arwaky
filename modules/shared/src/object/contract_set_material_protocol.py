"""Object domain contract: set material protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import SetMaterialVO


class SetMaterialProtocol(ABC):
    """Protocol interface for assigning or creating a material on an object."""

    @abstractmethod
    async def set_material(self, request: SetMaterialVO) -> SetMaterialVO:
        """Assign or create a material for an object."""
        ...
