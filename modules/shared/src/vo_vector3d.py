"""Immutable 3D vector with arithmetic and coordinate helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vector3D:
    """Immutable 3D vector with arithmetic and coordinate helpers."""

    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        if not all(isinstance(v, (int, float)) for v in (self.x, self.y, self.z)):
            raise TypeError("Vector3D coordinates must be numeric")

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3D:
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar: float) -> Vector3D:
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide Vector3D by zero")
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def magnitude(self) -> float:
        """Euclidean length from origin."""
        return float((self.x**2 + self.y**2 + self.z**2) ** 0.5)

    def as_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @staticmethod
    def from_list(vals: list[float]) -> Vector3D:
        if len(vals) != 3:
            raise ValueError(f"Expected 3 values for Vector3D, got {len(vals)}")
        return Vector3D(float(vals[0]), float(vals[1]), float(vals[2]))
