"""Object domain contract: set transform protocol (ABC).

Capability implements this protocol. The Agent layer depends on it;
the Surface layer depends on the Aggregate, not this Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import SetObjectTransformRequestVO
from .taxonomy_object_result_vo import TransformResultVO


class SetObjectTransformProtocol(ABC):
    """Protocol interface for modifying an object's transform."""

    @abstractmethod
    async def set_object_transform(
        self, request: SetObjectTransformRequestVO
    ) -> TransformResultVO:
        """Modify location, rotation, or scale of an existing object.

        FR-OBJ-003: Only sets provided transform fields; omitted fields are preserved.
        """
        ...
