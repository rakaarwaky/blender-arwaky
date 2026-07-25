"""Object domain contract: delete object protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import DeleteObjectRequestVO
from .taxonomy_object_result_vo import DeletionResultVO


class DeleteObjectProtocol(ABC):
    """Protocol interface for removing an object from the scene."""

    @abstractmethod
    async def delete_object(self, request: DeleteObjectRequestVO) -> DeletionResultVO:
        """Remove an object from the scene.

        FR-OBJ-006: Validates object exists, removes it via bpy.data.objects.remove().
        """
        ...
