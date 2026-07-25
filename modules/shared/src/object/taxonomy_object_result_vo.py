"""Object operation result Value Objects — structured responses for all 7 FRD operations."""

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
    RotationVector,
    ScaleVector,
    SuccessFlag,
)


@dataclass(frozen=True)
class PlacementResultVO:
    """Result from placing an asset or existing object in the scene."""

    success: SuccessFlag
    object_name: ObjectName
    asset_id: AssetId | None = None
    location: CoordinateList
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    message: str = ""


@dataclass(frozen=True)
class CreationResultVO:
    """Result from creating a primitive object."""

    success: SuccessFlag
    object_name: ObjectName
    primitive_type: ObjectType
    location: CoordinateList
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    message: str = ""


@dataclass(frozen=True)
class TransformResultVO:
    """Result from setting object transform."""

    success: SuccessFlag
    object_name: ObjectName
    location: CoordinateList | None = None
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    absolute_mode: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class MaterialResultVO:
    """Result from assigning or creating a material on an object."""

    success: SuccessFlag
    object_name: ObjectName
    material_name: MaterialName
    slot_index: int | None = None
    message: str = ""


@dataclass(frozen=True)
class ModifierResultVO:
    """Result from adding, updating, removing, or applying a modifier."""

    success: SuccessFlag
    object_name: ObjectName
    modifier_name: ModifierName
    modifier_type: ObjectType
    action: str = "add"
    applied_destructively: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class DeletionResultVO:
    """Result from deleting an object from the scene."""

    success: SuccessFlag
    deleted_count: ObjectCount
    deleted_names: list[ObjectName] = field(default_factory=list)
    children_handled: bool = False
    message: str = ""


@dataclass(frozen=True)
class ObjectInfoResultVO:
    """Result from retrieving detailed object information."""

    success: SuccessFlag
    object_name: ObjectName
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
