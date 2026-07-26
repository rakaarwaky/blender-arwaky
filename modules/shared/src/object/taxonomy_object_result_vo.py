"""Object operation result Value Objects.

Re-exports merged VOs from taxonomy_object_vo.py for backward compatibility.
"""

from .taxonomy_object_vo import (
    ApplyModifierVO,
    CreatePrimitiveVO,
    DeleteObjectVO,
    GetObjectInfoVO,
    PlaceAssetVO,
    SetMaterialVO,
    SetObjectTransformVO,
)

# Legacy aliases — prefer the merged VO names above
PlacementResultVO = PlaceAssetVO
CreationResultVO = CreatePrimitiveVO
TransformResultVO = SetObjectTransformVO
MaterialResultVO = SetMaterialVO
ModifierResultVO = ApplyModifierVO
DeletionResultVO = DeleteObjectVO
ObjectInfoResultVO = GetObjectInfoVO

__all__ = [
    "ApplyModifierVO",
    "CreatePrimitiveVO",
    "DeleteObjectVO",
    "GetObjectInfoVO",
    "PlaceAssetVO",
    "SetMaterialVO",
    "SetObjectTransformVO",
]
