"""BlenderObject domain entity.

Represents a Blender object with identity, spatial transforms, and
parent-child relationships. Validates on construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .constant_core_types import ObjectId, ObjectIdList, ObjectName, ObjectType, ScaleFactor
from .constant_object_types import ALLOWED_OBJECT_TYPES
from .vo_bounding_box import BoundingBox
from .vo_vector3d import Vector3D


@dataclass
class BlenderObject:
    """Domain entity representing a Blender object."""

    # Required fields (no defaults)
    name: ObjectName
    type: ObjectType  # Branded type for allowed Blender object types
    location: Vector3D
    rotation: Vector3D
    scale: Vector3D
    # Optional relationship fields (with defaults)
    parent_id: ObjectId | None = None
    children_ids: ObjectIdList = field(default_factory=lambda: ObjectIdList([]))
    # Identity (auto-generated if not provided)
    id: ObjectId = field(default_factory=lambda: ObjectId(uuid4()))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Object name cannot be empty")
        if not self.type:
            raise ValueError("Object type cannot be empty")
        if not isinstance(self.location, Vector3D):
            raise TypeError("location must be Vector3D")
        if not isinstance(self.rotation, Vector3D):
            raise TypeError("rotation must be Vector3D")
        if not isinstance(self.scale, Vector3D):
            raise TypeError("scale must be Vector3D")
        self.validate_type(ALLOWED_OBJECT_TYPES)

    def validate_type(self, allowed: list[ObjectType]) -> None:
        """Enforce that object type is in allowed set."""
        if self.type not in allowed:
            raise ValueError(f"Invalid object type '{self.type}'. Allowed: {allowed}")

    def translate(self, delta: Vector3D) -> None:
        """Move the object by a delta vector."""
        self.location = self.location + delta

    def rotate(self, delta: Vector3D) -> None:
        """Add rotation offset (Euler angles)."""
        self.rotation = self.rotation + delta

    def resize(self, sx: ScaleFactor, sy: ScaleFactor, sz: ScaleFactor) -> None:
        """Scale the object multiplicatively with individual factors."""
        self.scale = Vector3D(self.scale.x * sx, self.scale.y * sy, self.scale.z * sz)

    def parent_to(self, new_parent_id: UUID | None) -> None:
        """Change parentage — used by aggregate to maintain consistency."""
        if new_parent_id == self.id:
            raise ValueError("Object cannot parent to itself")
        self.parent_id = ObjectId(new_parent_id) if new_parent_id else None

    def add_child(self, child_id: UUID) -> None:
        """Add a child reference — aggregate maintains this."""
        wrapped = ObjectId(child_id)
        if wrapped not in self.children_ids:
            self.children_ids.append(wrapped)

    def remove_child(self, child_id: UUID) -> None:
        """Remove a child reference — aggregate maintains this."""
        wrapped = ObjectId(child_id)
        if wrapped in self.children_ids:
            self.children_ids.remove(wrapped)


def create_object_id(raw: UUID) -> ObjectId:
    """Factory helper to create an ObjectId from a UUID."""
    return ObjectId(raw)
