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
