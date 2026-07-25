"""Object operation request and response value objects."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    AssetId,
    CoordinateList,
    ObjectName,
    ObjectType,
    PrimitiveType,
    Progress,
    RotationVector,
    ScaleFactor,
    ScaleVector,
    SuccessFlag,
)


@dataclass(frozen=True)
class PlaceAssetRequestVO:
    """Request to place an asset in the scene."""

    asset_id: AssetId
    object_name: ObjectName | None = None
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None


@dataclass(frozen=True)
class PlaceAssetResponseVO:
    """Response from placing an asset."""

    success: SuccessFlag
    object_name: ObjectName
    asset_id: AssetId
    location: CoordinateList
    message: str


@dataclass(frozen=True)
class GetObjectInfoRequestVO:
    """Request to get object information."""

    object_name: ObjectName


@dataclass(frozen=True)
class GetObjectInfoResponseVO:
    """Response containing object information."""

    success: SuccessFlag
    object_info: object  # BlenderObject or similar
    message: str


@dataclass(frozen=True)
class SetObjectTransformRequestVO:
    """Request to set object transform."""

    object_name: ObjectName
    location: CoordinateList | None = None
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None


@dataclass(frozen=True)
class SetObjectTransformResponseVO:
    """Response from setting object transform."""

    success: SuccessFlag
    object_name: ObjectName
    message: str


@dataclass(frozen=True)
class DeleteObjectRequestVO:
    """Request to delete an object."""

    object_name: ObjectName


@dataclass(frozen=True)
class DeleteObjectResponseVO:
    """Response from deleting an object."""

    success: SuccessFlag
    object_name: ObjectName
    message: str


@dataclass(frozen=True)
class CreatePrimitiveRequestVO:
    """Request to create a primitive shape."""

    primitive_type: PrimitiveType
    name: ObjectName | None = None
    location: CoordinateList | None = None
    scale: ScaleVector | None = None


@dataclass(frozen=True)
class CreatePrimitiveResponseVO:
    """Response from creating a primitive."""

    success: SuccessFlag
    object_name: ObjectName
    primitive_type: PrimitiveType
    message: str


@dataclass(frozen=True)
class SetMaterialRequestVO:
    """Request to set material on an object."""

    object_name: ObjectName
    material_name: ObjectName


@dataclass(frozen=True)
class SetMaterialResponseVO:
    """Response from setting a material."""

    success: SuccessFlag
    object_name: ObjectName
    material_name: ObjectName
    message: str


@dataclass(frozen=True)
class ApplyModifierRequestVO:
    """Request to apply a modifier to an object."""

    object_name: ObjectName
    modifier_name: ObjectName


@dataclass(frozen=True)
class ApplyModifierResponseVO:
    """Response from applying a modifier."""

    success: SuccessFlag
    object_name: ObjectName
    modifier_name: ObjectName
    message: str
