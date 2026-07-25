"""Render operation request and response value objects."""

from __future__ import annotations

from dataclasses import dataclass

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
class GetScreenshotRequestVO:
    """Request to capture viewport screenshot."""

    max_size: int = 800
    view_angle: str | None = None
    shading: str | None = None
    show_overlays: bool = False
    focus_object: str | None = None
    format: ImageFormat | None = None


@dataclass(frozen=True)
class ScreenshotResponseVO:
    """Response containing screenshot data."""

    success: SuccessFlag
    image_data: ImageBytes
    format: ImageFormat
    width: ResolutionX
    height: ResolutionY


@dataclass(frozen=True)
class RenderRequestVO:
    """Request to render a frame."""

    output_path: str
    resolution_x: int | None = None
    resolution_y: int | None = None
    samples: RenderSamples | None = None
    use_denoising: UseDenoising | None = None


@dataclass(frozen=True)
class RenderResponseVO:
    """Response from a render operation."""

    success: SuccessFlag
    image_path: str
    render_time: float
    message: Prompt


@dataclass(frozen=True)
class CameraSetupRequestVO:
    """Request to configure a scene camera."""

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


@dataclass(frozen=True)
class HdriSetupRequestVO:
    """Request to configure HDRI environment lighting."""

    hdri_path: str
    strength: float = 1.0
    rotation: float = 0.0
    is_visible: bool = True
    overwrite_policy: str = "replace"


@dataclass(frozen=True)
class CameraConfigResultVO:
    """Result from camera configuration."""

    success: SuccessFlag
    camera_name: str
    final_settings: dict
    message: Prompt


@dataclass(frozen=True)
class HdriConfigResultVO:
    """Result from HDRI configuration."""

    success: SuccessFlag
    environment_ref: str
    applied_strength: float
    message: Prompt
