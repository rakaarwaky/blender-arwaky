"""Object operation request and response value objects.

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
PlaceAssetRequestVO = PlaceAssetVO
PlaceAssetResponseVO = PlaceAssetVO
PlaceAssetResultVO = PlaceAssetVO
GetObjectInfoRequestVO = GetObjectInfoVO
GetObjectInfoResponseVO = GetObjectInfoVO
GetObjectInfoResultVO = GetObjectInfoVO
SetObjectTransformRequestVO = SetObjectTransformVO
SetObjectTransformResponseVO = SetObjectTransformVO
SetObjectTransformResultVO = SetObjectTransformVO
DeleteObjectRequestVO = DeleteObjectVO
DeleteObjectResponseVO = DeleteObjectVO
DeleteObjectResultVO = DeleteObjectVO
CreatePrimitiveRequestVO = CreatePrimitiveVO
CreatePrimitiveResponseVO = CreatePrimitiveVO
CreatePrimitiveResultVO = CreatePrimitiveVO
SetMaterialRequestVO = SetMaterialVO
SetMaterialResponseVO = SetMaterialVO
SetMaterialResultVO = SetMaterialVO
ApplyModifierRequestVO = ApplyModifierVO
ApplyModifierResponseVO = ApplyModifierVO
ApplyModifierResultVO = ApplyModifierVO

__all__ = [
    "ApplyModifierVO",
    "CreatePrimitiveVO",
    "DeleteObjectVO",
    "GetObjectInfoVO",
    "PlaceAssetVO",
    "SetMaterialVO",
    "SetObjectTransformVO",
]
