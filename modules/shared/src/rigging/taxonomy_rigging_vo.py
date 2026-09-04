"""Rigging and deformation value objects shared across AES layers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ArmatureStateVO:
    object_name: str
    bone_count: int
    bones: tuple[dict[str, object], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RiggingMutationVO:
    object_name: str | None
    changed: bool
    operation: str
    bone_name: str | None = None
    constraint_name: str | None = None
    shape_key_name: str | None = None
    message: str = ""


@dataclass(frozen=True)
class DeformationStateVO:
    object_name: str
    armature_modifiers: tuple[dict[str, object], ...] = field(default_factory=tuple)
    constraints: tuple[dict[str, object], ...] = field(default_factory=tuple)
    shape_keys: tuple[dict[str, object], ...] = field(default_factory=tuple)
