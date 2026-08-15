"""Physics value objects shared across AES layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicsStateVO:
    object_name: str
    rigid_body_enabled: bool
    rigid_body_type: str | None
    rigid_body_mass: float | None
    rigid_body_kinematic: bool | None
    cloth_enabled: bool
    cloth_quality: int | None
    cloth_pin_group: str | None


@dataclass(frozen=True)
class PhysicsMutationVO:
    object_name: str | None
    changed: bool
    operation: str
    body_type: str | None = None
    mass: float | None = None
    quality: int | None = None
    frame_start: int | None = None
    frame_end: int | None = None
    message: str = ""
