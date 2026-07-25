"""Axis-aligned bounding box defined by min and max corners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .taxonomy_vector3d_vo import Vector3D


@dataclass(frozen=True)
class BoundingBox:
    """Axis-aligned bounding box defined by min and max corners."""

    min: Vector3D
    max: Vector3D

    def __post_init__(self) -> None:
        for coord in ("x", "y", "z"):
            min_val = getattr(self.min, coord)
            max_val = getattr(self.max, coord)
            if min_val > max_val:
                raise ValueError(f"BoundingBox min.{coord} ({min_val}) cannot exceed max.{coord} ({max_val})")

    def dimensions(self) -> Vector3D:
        return Vector3D(
            self.max.x - self.min.x,
            self.max.y - self.min.y,
            self.max.z - self.min.z,
        )

    def expand(self, point: Vector3D) -> BoundingBox:
        new_min = Vector3D(
            min(self.min.x, point.x),
            min(self.min.y, point.y),
            min(self.min.z, point.z),
        )
        new_max = Vector3D(
            max(self.max.x, point.x),
            max(self.max.y, point.y),
            max(self.max.z, point.z),
        )
        return BoundingBox(new_min, new_max)

    def merge(self, other: BoundingBox) -> BoundingBox:
        new_min = Vector3D(
            min(self.min.x, other.min.x),
            min(self.min.y, other.min.y),
            min(self.min.z, other.min.z),
        )
        new_max = Vector3D(
            max(self.max.x, other.max.x),
            max(self.max.y, other.max.y),
            max(self.max.z, other.max.z),
        )
        return BoundingBox(new_min, new_max)

    def contains(self, point: Vector3D) -> bool:
        return (
            self.min.x <= point.x <= self.max.x
            and self.min.y <= point.y <= self.max.y
            and self.min.z <= point.z <= self.max.z
        )

    def volume(self) -> float:
        return (self.max.x - self.min.x) * (self.max.y - self.min.y) * (self.max.z - self.min.z)

    def to_dict(self) -> dict[str, Any]:
        return {"min": self.min.as_dict(), "max": self.max.as_dict()}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BoundingBox:
        return BoundingBox(
            Vector3D(data["min"]["x"], data["min"]["y"], data["min"]["z"]),
            Vector3D(data["max"]["x"], data["max"]["y"], data["max"]["z"]),
        )
