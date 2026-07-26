"""Render operation value objects — unified input/output per operation.

Each VO merges request (input) and response (output) into a single frozen dataclass.
Caller sets input fields; callee sets output fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    ImageBytes,
    ImageFormat,
    Prompt,
    RenderSamples,
    ResolutionX,
    ResolutionY,
    SuccessFlag,
    UseDenoising,
)


@dataclass(frozen=True)
class GetScreenshotVO:
    """Screenshot capture — input and output in one VO.

    Input: max_size, view_angle, shading, show_overlays, focus_object, format.
    Output: success, image_data, format, width, height.
    """
    # Input
    max_size: int = 800
    view_angle: str | None = None
    shading: str | None = None
    show_overlays: bool = False
    focus_object: str | None = None
    format: ImageFormat | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    image_data: ImageBytes = field(default_factory=lambda: ImageBytes(b""))
    width: ResolutionX = field(default_factory=lambda: ResolutionX(0))
    height: ResolutionY = field(default_factory=lambda: ResolutionY(0))


@dataclass(frozen=True)
class RenderVO:
    """Render frame — input and output in one VO.

    Input: output_path, resolution_x, resolution_y, samples, use_denoising.
    Output: success, image_path, render_time, message.
    """
    # Input
    output_path: str
    resolution_x: int | None = None
    resolution_y: int | None = None
    samples: RenderSamples | None = None
    use_denoising: UseDenoising | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    image_path: str = ""
    render_time: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class CameraSetupVO:
    """Camera setup — input and output in one VO.

    Input: camera_name, location, rotation, focal_length, is_active, framing_target.
    Output: success, message.
    """
    # Input
    camera_name: str | None = None
    location_x: float = 0.0
    location_y: float = 0.0
    location_z: float = 0.0
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    focal_length: float = 50.0
    is_active: bool = False
    framing_target: str | None = None
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class HdriSetupVO:
    """HDRI setup — input and output in one VO.

    Input: hdri_path, strength, rotation, is_visible, overwrite_policy.
    Output: success, environment_ref, applied_strength, message.
    """
    # Input
    hdri_path: str
    strength: float = 1.0
    rotation: float = 0.0
    is_visible: bool = True
    overwrite_policy: str = "replace"
    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    environment_ref: str = ""
    applied_strength: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class CameraConfigVO:
    """Camera configuration result — output only (no separate request)."""
    success: SuccessFlag = field(default=SuccessFlag(False))
    camera_name: str = ""
    final_settings: dict = field(default_factory=dict)
    message: Prompt = field(default_factory=lambda: Prompt(""))


@dataclass(frozen=True)
class HdriConfigVO:
    """HDRI configuration result — output only (no separate request)."""
    success: SuccessFlag = field(default=SuccessFlag(False))
    environment_ref: str = ""
    applied_strength: float = 0.0
    message: Prompt = field(default_factory=lambda: Prompt(""))