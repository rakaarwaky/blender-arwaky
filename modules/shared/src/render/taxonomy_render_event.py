"""Render taxonomy events."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.taxonomy_core_vo import (
    DurationMs,
    EnabledFlag,
    FilePath,
    ImageFormat,
    LightStrength,
    ObjectName,
    Prompt,
    RenderEngine,
    RenderTime,
    RequestId,
    ResolutionX,
    ResolutionY,
    SuccessFlag,
    TaskUuid,
    UseDenoising,
)
from .taxonomy_render_error import RenderErrorCategory
from .taxonomy_render_vo import FocalLength, RotationDegrees


@dataclass(frozen=True)
class ViewportCapturedEvent:
    """Emitted when viewport capture completes."""

    correlation_id: RequestId
    success: SuccessFlag
    artifact_path: FilePath
    image_format: ImageFormat
    width: ResolutionX
    height: ResolutionY
    duration_ms: DurationMs
    message: Prompt


@dataclass(frozen=True)
class SceneRenderCompletedEvent:
    """Emitted when scene render completes."""

    correlation_id: RequestId
    success: SuccessFlag
    artifact_path: FilePath
    render_time: RenderTime
    final_resolution_x: ResolutionX
    final_resolution_y: ResolutionY
    engine_used: RenderEngine
    denoising_applied: UseDenoising
    task_ref: TaskUuid | None
    message: Prompt


@dataclass(frozen=True)
class SceneRenderFailedEvent:
    """Emitted when scene render fails."""

    correlation_id: RequestId
    success: SuccessFlag
    error_category: RenderErrorCategory
    phase: str
    message: Prompt


@dataclass(frozen=True)
class RenderSubmittedToBackgroundEvent:
    """Emitted when render is submitted to background job."""

    correlation_id: RequestId
    success: SuccessFlag
    task_ref: TaskUuid
    message: Prompt


@dataclass(frozen=True)
class CameraConfiguredEvent:
    """Emitted when camera configuration completes."""

    correlation_id: RequestId
    success: SuccessFlag
    camera_ref: ObjectName
    focal_length: FocalLength
    active_status: EnabledFlag
    depth_of_field_applied: EnabledFlag
    message: Prompt


@dataclass(frozen=True)
class HdriLightingConfiguredEvent:
    """Emitted when HDRI lighting configuration completes."""

    correlation_id: RequestId
    success: SuccessFlag
    environment_ref: ObjectName
    strength: LightStrength
    rotation: RotationDegrees
    message: Prompt
