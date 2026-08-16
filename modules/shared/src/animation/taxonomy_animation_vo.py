from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnimationKeyframeVO:
    frame: float
    value: float
    index: int


@dataclass(frozen=True)
class AnimationCurveVO:
    data_path: str
    array_index: int
    keyframes: tuple[AnimationKeyframeVO, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AnimationStateVO:
    object_name: str
    action_name: str | None
    frame_start: int
    frame_end: int
    current_frame: int
    curves: tuple[AnimationCurveVO, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AnimationMutationVO:
    object_name: str
    data_path: str | None = None
    frame: int | None = None
    changed: bool = True
    frame_start: int | None = None
    frame_end: int | None = None
    current_frame: int | None = None


@dataclass(frozen=True)
class AnimationActionVO:
    name: str
    frame_start: float
    frame_end: float
    curve_count: int
    slot_count: int = 0


@dataclass(frozen=True)
class RigifyControlVO:
    name: str
    role: str
    side: str | None
    is_deform: bool


@dataclass(frozen=True)
class RigifyControlStateVO:
    armature_name: str
    controls: tuple[RigifyControlVO, ...] = field(default_factory=tuple)
    control_count: int = 0


@dataclass(frozen=True)
class AnimationImportVO:
    source_path: str
    importer: str
    imported_objects: tuple[str, ...] = field(default_factory=tuple)
    action_names: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AnimationActionLinkVO:
    armature_name: str
    action_name: str
    previous_action_name: str | None
    changed: bool


@dataclass(frozen=True)
class AnimationPoseAssetVO:
    name: str
    is_pose_asset: bool
    frame_start: float
    frame_end: float
    catalog_id: str | None = None


@dataclass(frozen=True)
class AnimationPoseAssetStateVO:
    armature_name: str
    asset_name: str
    blend_factor: float
    flipped: bool
    changed: bool


@dataclass(frozen=True)
class AnimationPoseBufferVO:
    armature_name: str
    flipped: bool
    selected_mask: bool
    changed: bool


@dataclass(frozen=True)
class RigifyPoseKeyframeVO:
    armature_name: str
    frame: int
    bone_names: tuple[str, ...] = field(default_factory=tuple)
    changed: bool = True
