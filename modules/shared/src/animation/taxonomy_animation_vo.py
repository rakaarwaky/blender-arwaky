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
class ShapeKeyKeyframeVO:
    mesh_name: str
    shape_key_name: str
    value: float
    frame: int
    changed: bool


@dataclass(frozen=True)
class NlaTrackVO:
    armature_name: str
    track_name: str
    strip_count: int
    is_solo: bool
    is_muted: bool
    changed: bool


@dataclass(frozen=True)
class NlaStripVO:
    armature_name: str
    track_name: str
    strip_name: str
    action_name: str
    frame_start: float
    frame_end: float
    scale: float
    repeat: float
    blend_in: float
    blend_out: float
    influence: float
    blend_type: str
    extrapolation: str
    reversed: bool
    changed: bool


@dataclass(frozen=True)
class NlaLayerVO:
    armature_name: str
    track_name: str
    blend_type: str | None
    influence: float | None
    is_solo: bool | None
    is_muted: bool | None
    changed: bool


@dataclass(frozen=True)
class NlaMaskVO:
    armature_name: str
    track_name: str
    strip_name: str
    bone_names: tuple[str, ...] = field(default_factory=tuple)
    changed: bool = True


@dataclass(frozen=True)
class NlaBakeVO:
    armature_name: str
    output_action: str
    frame_start: int
    frame_end: int
    step: int
    keyframe_count: int
    cleared_constraints: bool
    cleared_nla: bool
    changed: bool


@dataclass(frozen=True)
class NlaValidationVO:
    armature_name: str
    track_count: int
    strip_count: int
    frame_start: float | None
    frame_end: float | None
    approved: bool
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NlaMutationVO:
    armature_name: str
    track_name: str
    strip_name: str | None
    changed: bool
    removed: bool = False
