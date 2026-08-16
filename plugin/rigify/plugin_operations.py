from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RigifyInspectArmatureRequest:
    """Validated request for inspecting one armature through the Blender bridge."""

    object_name: str
    limit: int = 100

    def __post_init__(self) -> None:
        name = str(self.object_name).strip()
        if not name or len(name) > 128 or any(ord(char) < 32 for char in name):
            raise ValueError("object_name must contain 1-128 printable characters")
        if not 1 <= int(self.limit) <= 1000:
            raise ValueError("limit must be between 1 and 1000")


def map_inspect_armature(request: RigifyInspectArmatureRequest) -> dict[str, object]:
    """Map a validated Rigify request to the canonical Blender command."""
    return {
        "type": "inspect_armature",
        "params": {
            "object_name": str(request.object_name).strip(),
            "limit": int(request.limit),
        },
    }


@dataclass(frozen=True)
class RigifyPoseBoneTransformRequest:
    """Validated request for changing one pose-bone transform."""

    armature_name: str
    bone_name: str
    location: list[float] | None = None
    rotation_euler: list[float] | None = None
    scale: list[float] | None = None

    def __post_init__(self) -> None:
        _validate_name(self.armature_name, "armature_name")
        _validate_name(self.bone_name, "bone_name")
        vectors = {
            "location": self.location,
            "rotation_euler": self.rotation_euler,
            "scale": self.scale,
        }
        if all(value is None for value in vectors.values()):
            raise ValueError("at least one pose transform vector is required")
        for name, value in vectors.items():
            if value is not None:
                _validate_vector(value, name)


def map_set_pose_bone_transform(request: RigifyPoseBoneTransformRequest) -> dict[str, object]:
    """Map a validated pose request to the canonical Blender command."""
    return {
        "type": "set_pose_bone_transform",
        "params": {
            "armature_name": str(request.armature_name).strip(),
            "bone_name": str(request.bone_name).strip(),
            "location": request.location,
            "rotation_euler": request.rotation_euler,
            "scale": request.scale,
        },
    }


def _validate_name(value: str, name: str) -> None:
    """Validate a Blender datablock or bone name."""
    normalized = str(value).strip()
    if not normalized or len(normalized) > 128 or any(ord(char) < 32 for char in normalized):
        raise ValueError(f"{name} must contain 1-128 printable characters")


def _validate_vector(value: list[float], name: str) -> None:
    """Validate one finite three-number transform vector."""
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{name} must contain exactly 3 numbers")
    if not all(isinstance(item, (int, float)) and math.isfinite(float(item)) for item in value):
        raise ValueError(f"{name} must contain finite numbers")


RIGIFY_ALLOWED_CONSTRAINT_TYPES = (
    "COPY_LOCATION",
    "COPY_ROTATION",
    "LIMIT_LOCATION",
    "LIMIT_ROTATION",
)


@dataclass(frozen=True)
class RigifyBoneConstraintRequest:
    """Validated request for configuring one pose-bone constraint."""

    armature_name: str
    bone_name: str
    constraint_type: str
    enabled: bool
    constraint_name: str | None = None
    target_object: str | None = None
    subtarget: str | None = None

    def __post_init__(self) -> None:
        _validate_name(self.armature_name, "armature_name")
        _validate_name(self.bone_name, "bone_name")
        constraint_type = str(self.constraint_type).upper()
        if constraint_type not in RIGIFY_ALLOWED_CONSTRAINT_TYPES:
            raise ValueError(f"unsupported constraint type: {constraint_type}")
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be boolean")
        for name, value in {
            "constraint_name": self.constraint_name,
            "target_object": self.target_object,
            "subtarget": self.subtarget,
        }.items():
            if value is not None:
                _validate_name(value, name)


def map_configure_bone_constraint(request: RigifyBoneConstraintRequest) -> dict[str, object]:
    """Map a validated constraint request to the canonical Blender command."""
    return {
        "type": "configure_bone_constraint",
        "params": {
            "armature_name": str(request.armature_name).strip(),
            "bone_name": str(request.bone_name).strip(),
            "constraint_type": str(request.constraint_type).upper(),
            "enabled": request.enabled,
            "constraint_name": request.constraint_name,
            "target_object": request.target_object,
            "subtarget": request.subtarget,
        },
    }
