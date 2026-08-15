"""Animation value objects shared across the dispatcher and feature layers."""

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
