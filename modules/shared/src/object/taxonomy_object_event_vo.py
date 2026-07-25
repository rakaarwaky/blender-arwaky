"""Object domain events — immutable facts about object state changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from ..common.taxonomy_core_vo import (
    AssetId,
    CoordinateList,
    MaterialName,
    ModifierName,
    ObjectId,
    ObjectName,
    ObjectType,
    RotationVector,
    ScaleVector,
    SuccessFlag,
    Timestamp,
)


@dataclass(frozen=True)
class ObjectCreatedEvent:
    """Emitted when a primitive object is created."""

    object_id: ObjectId
    object_name: ObjectName
    primitive_type: ObjectType
    location: CoordinateList
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


@dataclass(frozen=True)
class ObjectPlacedEvent:
    """Emitted when an asset or existing object is placed in the scene."""

    object_id: ObjectId
    object_name: ObjectName
    asset_id: AssetId | None = None
    location: CoordinateList
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


@dataclass(frozen=True)
class ObjectTransformedEvent:
    """Emitted when an object's transform is modified."""

    object_id: ObjectId
    object_name: ObjectName
    location: CoordinateList | None = None
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    absolute_mode: SuccessFlag = field(default=SuccessFlag(False))
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


@dataclass(frozen=True)
class ObjectMaterialAssignedEvent:
    """Emitted when a material is assigned to an object."""

    object_id: ObjectId
    object_name: ObjectName
    material_name: MaterialName
    slot_index: int | None = None
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


@dataclass(frozen=True)
class ObjectModifierAddedEvent:
    """Emitted when a modifier is added or updated on an object."""

    object_id: ObjectId
    object_name: ObjectName
    modifier_name: ModifierName
    modifier_type: ObjectType
    action: str = "add"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


@dataclass(frozen=True)
class ObjectDeletedEvent:
    """Emitted when an object is removed from the scene."""

    object_id: ObjectId
    object_name: ObjectName
    deleted_by_user: SuccessFlag = field(default=SuccessFlag(True))
    children_handled: SuccessFlag = field(default=SuccessFlag(False))
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


@dataclass(frozen=True)
class ObjectInfoRetrievedEvent:
    """Emitted when object information is successfully retrieved."""

    object_id: ObjectId
    object_name: ObjectName
    detail_level: str = "full"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(float("nan")))


def generate_object_event_id() -> UUID:
    """Generate a unique identifier for an object domain event."""
    return uuid4()
