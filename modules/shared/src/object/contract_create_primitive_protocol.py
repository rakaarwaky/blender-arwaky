"""Object domain contract: create primitive protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import CreatePrimitiveVO


class CreatePrimitiveProtocol(ABC):
    """Protocol interface for creating a basic geometric primitive.

    FR-OBJ-002: Create Primitive
    """

    @abstractmethod
    async def create_primitive(self, request: CreatePrimitiveVO) -> CreatePrimitiveVO:
        """Create a basic geometric or scene primitive."""
        ...
