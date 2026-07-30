"""BlenderObject domain entity.

Represents a Blender object with identity, spatial transforms, and
parent-child relationships. Validates on construction.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from ..common.taxonomy_core_vo import ObjectId, ObjectIdList, ObjectName, ObjectType, ScaleFactor
from ..common.taxonomy_vector3d_vo import Vector3D
from .taxonomy_object_constant import ALLOWED_OBJECT_TYPES


@dataclass
class BlenderObject:
    """Domain entity representing a Blender object."""

    name: ObjectName
    type: ObjectType
    location: Vector3D
    rotation: Vector3D
    scale: Vector3D
    parent_id: ObjectId | None = None
    children_ids: ObjectIdList = field(default_factory=lambda: ObjectIdList([]))
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

    def validate_type(self, allowed: Iterable[str]) -> None:
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

    def parent_to(self, new_parent_id: ObjectId | None) -> None:
        """Change parentage — used by aggregate to maintain consistency."""
        if new_parent_id == self.id:
            raise ValueError("Object cannot parent to itself")
        self.parent_id = new_parent_id

    def add_child(self, child_id: ObjectId) -> None:
        """Add a child reference — aggregate maintains this."""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)

    def remove_child(self, child_id: ObjectId) -> None:
        """Remove a child reference — aggregate maintains this."""
        if child_id in self.children_ids:
            self.children_ids.remove(child_id)


def create_object_id(raw: Any) -> ObjectId:
    """Factory helper to create an ObjectId from a raw UUID or string."""
    return ObjectId(raw)
