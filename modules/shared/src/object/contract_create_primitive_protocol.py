"""Object domain contract: create primitive protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import CreatePrimitiveRequestVO
from .taxonomy_object_result_vo import CreationResultVO


class CreatePrimitiveProtocol(ABC):
    """Protocol interface for creating a basic geometric primitive."""

    @abstractmethod
    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreationResultVO:
        """Create a basic geometric or scene primitive.

        FR-OBJ-002: Validates primitive type, resolves operator string,
        generates and executes Blender Python code.
        """
        ...
