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


@dataclass(frozen=True)
class RigifyDeformationStateRequest:
    """Validated request for inspecting one mesh deformation state."""

    object_name: str

    def __post_init__(self) -> None:
        _validate_name(self.object_name, "object_name")


def map_get_deformation_state(request: RigifyDeformationStateRequest) -> dict[str, object]:
    """Map a validated deformation request to the canonical Blender command."""
    return {
        "type": "get_deformation_state",
        "params": {"object_name": str(request.object_name).strip()},
    }


@dataclass(frozen=True)
class RigifyShapeKeyRequest:
    """Validated request for creating, updating, or removing one shape key."""

    object_name: str
    shape_key_name: str
    enabled: bool
    value: float = 0.0
    slider_min: float = 0.0
    slider_max: float = 1.0

    def __post_init__(self) -> None:
        _validate_name(self.object_name, "object_name")
        _validate_name(self.shape_key_name, "shape_key_name")
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be boolean")
        values = {
            "value": self.value,
            "slider_min": self.slider_min,
            "slider_max": self.slider_max,
        }
        for name, value in values.items():
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"{name} must be a finite number")
            if not -10.0 <= float(value) <= 10.0:
                raise ValueError(f"{name} must be between -10.0 and 10.0")
        if float(self.slider_min) > float(self.slider_max):
            raise ValueError("slider_min must be less than or equal to slider_max")
        if not float(self.slider_min) <= float(self.value) <= float(self.slider_max):
            raise ValueError("value must be within slider limits")


def map_configure_shape_key(request: RigifyShapeKeyRequest) -> dict[str, object]:
    """Map a validated shape-key request to the canonical Blender command."""
    return {
        "type": "configure_shape_key",
        "params": {
            "object_name": str(request.object_name).strip(),
            "shape_key_name": str(request.shape_key_name).strip(),
            "enabled": request.enabled,
            "value": float(request.value),
            "slider_min": float(request.slider_min),
            "slider_max": float(request.slider_max),
        },
    }


@dataclass(frozen=True)
class RigifyCharacterBindingRequest:
    """Validated request for binding a character mesh to a Rigify armature."""

    character_object_name: str
    armature_name: str
    modifier_name: str | None = None
    replace_existing: bool = False

    def __post_init__(self) -> None:
        _validate_name(self.character_object_name, "character_object_name")
        _validate_name(self.armature_name, "armature_name")
        if self.modifier_name is not None:
            _validate_name(self.modifier_name, "modifier_name")
        if not isinstance(self.replace_existing, bool):
            raise ValueError("replace_existing must be boolean")


def map_bind_character_to_rig(request: RigifyCharacterBindingRequest) -> dict[str, object]:
    """Map a validated character binding request to the canonical Blender command."""
    return {
        "type": "bind_character_to_rig",
        "params": {
            "character_object_name": str(request.character_object_name).strip(),
            "armature_name": str(request.armature_name).strip(),
            "modifier_name": str(request.modifier_name).strip() if request.modifier_name else "Rigify_Armature",
            "replace_existing": request.replace_existing,
        },
    }
