"""Object domain contract: aggregate facade (ABC).

Aggregates all object operations into a single facade that the Agent
layer consumes. Surface layer depends on this aggregate.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_object_vo import (
    ApplyModifierVO,
    CreatePrimitiveVO,
    DeleteObjectVO,
    GetObjectInfoVO,
    PlaceAssetVO,
    SetMaterialVO,
    SetObjectTransformVO,
)


class ObjectOperateAggregate(ABC):
    """Aggregate facade for object-level manipulation in Blender."""

    @abstractmethod
    async def place_asset(self, request: PlaceAssetVO) -> PlaceAssetVO:
        """Position an existing object or imported asset at target transform."""
        ...

    @abstractmethod
    async def create_primitive(self, request: CreatePrimitiveVO) -> CreatePrimitiveVO:
        """Create a basic geometric or scene primitive."""
        ...

    @abstractmethod
    async def set_object_transform(self, request: SetObjectTransformVO) -> SetObjectTransformVO:
        """Modify location, rotation, or scale of an existing object."""
        ...

    @abstractmethod
    async def set_material(self, request: SetMaterialVO) -> SetMaterialVO:
        """Assign or create a material for an object."""
        ...

    @abstractmethod
    async def apply_modifier(self, request: ApplyModifierVO) -> ApplyModifierVO:
        """Add, update, remove, or apply a modifier on an object."""
        ...

    @abstractmethod
    async def delete_object(self, request: DeleteObjectVO) -> DeleteObjectVO:
        """Remove an object from the scene."""
        ...

    @abstractmethod
    async def get_object_info(self, request: GetObjectInfoVO) -> GetObjectInfoVO:
        """Retrieve detailed information about a specific object."""
        ...
