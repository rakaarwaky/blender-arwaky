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


@dataclass(frozen=True)
class SimulationStateVO:
    object_name: str
    particle_system_count: int
    particle_systems: tuple[dict[str, object], ...]
    force_field_enabled: bool
    force_field_type: str | None
    force_field_strength: float | None
    fluid_domain_enabled: bool
    fluid_domain_type: str | None
    fluid_resolution: int | None
    fluid_cache_type: str | None


@dataclass(frozen=True)
class SimulationCacheStatusVO:
    frame_start: int
    frame_end: int
    current_frame: int
    cache_states: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class SimulationMutationVO:
    object_name: str | None
    changed: bool
    operation: str
    particle_system_name: str | None = None
    force_field_type: str | None = None
    fluid_domain_type: str | None = None
    message: str = ""
