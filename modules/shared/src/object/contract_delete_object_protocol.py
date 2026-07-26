"""Object domain contract: delete object protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import DeleteObjectVO


class DeleteObjectProtocol(ABC):
    """Protocol interface for removing an object from the scene."""

    @abstractmethod
    async def delete_object(self, request: DeleteObjectVO) -> DeleteObjectVO:
        """Remove an object from the scene."""
        ...
