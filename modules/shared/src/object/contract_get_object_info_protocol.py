"""Object domain contract: get object info protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import GetObjectInfoRequestVO
from .taxonomy_object_result_vo import ObjectInfoResultVO


class GetObjectInfoProtocol(ABC):
    """Protocol interface for retrieving detailed object information."""

    @abstractmethod
    async def get_object_info(
        self, request: GetObjectInfoRequestVO
    ) -> ObjectInfoResultVO:
        """Retrieve detailed information about a specific object.

        FR-OBJ-007: Delegates to code executor for scene introspection.
        Returns structured info about the object's state.
        """
        ...
