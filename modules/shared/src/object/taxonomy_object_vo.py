"""Object operation value objects — unified input/output per operation.

Each VO merges request (input) and result (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..common.taxonomy_core_vo import (
    AssetId,
    CoordinateList,
    MaterialName,
    ModifierName,
    ObjectCount,
    ObjectName,
    ObjectType,
    PrimitiveType,
    RotationVector,
    ScaleVector,
    SuccessFlag,
)


@dataclass(frozen=True)
class PlaceAssetVO:
    """Place asset — input and output in one VO.

    Input: asset_id, object_name, location, rotation, scale.
    Output: success, message.
    """
    # Input
    asset_id: AssetId
    object_name: ObjectName | None = None
    location: CoordinateList = field(default_factory=lambda: CoordinateList([0.0, 0.0, 0.0]))
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class GetObjectInfoVO:
    """Get object info — input and output in one VO.

    Input: object_name.
    Output: success, object_type, location, rotation, scale, parent_name, etc.
    """
    # Input
    object_name: ObjectName
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    object_type: ObjectType | None = None
    location: CoordinateList | None = None
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    parent_name: ObjectName | None = None
    collection_names: list[ObjectName] = field(default_factory=list)
    material_names: list[MaterialName] = field(default_factory=list)
    modifier_summaries: list[dict[str, Any]] = field(default_factory=list)
    visibility: bool = True
    detail_level: str = "full"
    message: str = ""


@dataclass(frozen=True)
class SetObjectTransformVO:
    """Set object transform — input and output in one VO.

    Input: object_name, location, rotation, scale.
    Output: success, message.
    """
    # Input
    object_name: ObjectName
    location: CoordinateList | None = None
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    absolute_mode: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class DeleteObjectVO:
    """Delete object — input and output in one VO.

    Input: object_name.
    Output: success, deleted_count, deleted_names, children_handled, message.
    """
    # Input
    object_name: ObjectName
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    deleted_count: ObjectCount = field(default_factory=lambda: ObjectCount(0))
    deleted_names: list[ObjectName] = field(default_factory=list)
    children_handled: bool = False
    message: str = ""


@dataclass(frozen=True)
class CreatePrimitiveVO:
    """Create primitive — input and output in one VO.

    Input: primitive_type, name, location, scale.
    Output: success, object_name, message.
    """
    # Input
    primitive_type: PrimitiveType
    name: ObjectName | None = None
    location: CoordinateList | None = None
    scale: ScaleVector | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    object_name: ObjectName = field(default_factory=lambda: ObjectName(""))
    message: str = ""


@dataclass(frozen=True)
class SetMaterialVO:
    """Set material — input and output in one VO.

    Input: object_name, material_name.
    Output: success, slot_index, message.
    """
    # Input
    object_name: ObjectName
    material_name: MaterialName
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    slot_index: int | None = None
    message: str = ""


@dataclass(frozen=True)
class ApplyModifierVO:
    """Apply modifier — input and output in one VO.

    Input: object_name, modifier_name.
    Output: success, modifier_type, action, applied_destructively, message.
    """
    # Input
    object_name: ObjectName
    modifier_name: ModifierName
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    modifier_type: ObjectType = field(default_factory=lambda: ObjectType(""))
    action: str = "add"
    applied_destructively: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""
