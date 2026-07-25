"""Object domain contract: aggregate facade (ABC).

Aggregates ObjectOperateProtocol methods into a single facade that the Agent
layer consumes. Surface layer depends on this aggregate, not on concrete Capabilities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_request_vo import (
    ApplyModifierRequestVO,
    CreatePrimitiveRequestVO,
    DeleteObjectRequestVO,
    GetObjectInfoRequestVO,
    PlaceAssetRequestVO,
    SetMaterialRequestVO,
    SetObjectTransformRequestVO,
)
from .taxonomy_object_result_vo import (
    CreationResultVO,
    DeletionResultVO,
    MaterialResultVO,
    ModifierResultVO,
    ObjectInfoResultVO,
    PlacementResultVO,
    TransformResultVO,
)


class ObjectOperateAggregate(ABC):
    """Aggregate facade for object-level manipulation in Blender.

    This interface is implemented by the Agent orchestrator and consumed
    by the Surface layer. Capabilities implement ObjectOperateProtocol;
    the aggregate delegates to them.
    """

    @abstractmethod
    async def place_asset(self, request: PlaceAssetRequestVO) -> PlacementResultVO:
        """Position an existing object or imported asset at target transform."""
        pass

    @abstractmethod
    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreationResultVO:
        """Create a basic geometric or scene primitive."""
        pass

    @abstractmethod
    async def set_object_transform(self, request: SetObjectTransformRequestVO) -> TransformResultVO:
        """Modify location, rotation, or scale of an existing object."""
        pass

    @abstractmethod
    async def set_material(self, request: SetMaterialRequestVO) -> MaterialResultVO:
        """Assign or create a material for an object."""
        pass

    @abstractmethod
    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ModifierResultVO:
        """Add, update, remove, or apply a modifier on an object."""
        pass

    @abstractmethod
    async def delete_object(self, request: DeleteObjectRequestVO) -> DeletionResultVO:
        """Remove an object from the scene."""
        pass

    @abstractmethod
    async def get_object_info(self, request: GetObjectInfoRequestVO) -> ObjectInfoResultVO:
        """Retrieve detailed information about a specific object."""
        pass
