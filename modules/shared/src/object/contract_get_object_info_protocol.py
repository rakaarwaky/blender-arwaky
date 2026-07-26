"""Object domain contract: get object info protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import GetObjectInfoVO


class GetObjectInfoProtocol(ABC):
    """Protocol interface for retrieving detailed object information."""

    @abstractmethod
    async def get_object_info(self, request: GetObjectInfoVO) -> GetObjectInfoVO:
        """Retrieve detailed information about a specific object."""
        ...
