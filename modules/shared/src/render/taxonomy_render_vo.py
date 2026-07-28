"""Render taxonomy value objects.

Unified request/response VOs per operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NewType

from ..common.taxonomy_core_vo import (
    DurationMs,
    EnabledFlag,
    FilePath,
    ImageFormat,
    LightStrength,
    MaxImageSize,
    ObjectName,
    Prompt,
    RenderEngine,
    RenderSamples,
    RenderTime,
    RequestId,
    ResolutionX,
    ResolutionY,
    SuccessFlag,
    TaskUuid,
    UseDenoising,
)
from .taxonomy_render_constant import (
    CAMERA_SENSOR_FIT_AUTO,
    DEFAULT_APERTURE,
    DEFAULT_FOCAL_LENGTH,
    DEFAULT_HDRI_ROTATION,
    DEFAULT_HDRI_STRENGTH,
    DEFAULT_MAX_IMAGE_SIZE,
    DEFAULT_RESOLUTION_X,
    DEFAULT_RESOLUTION_Y,
    DEFAULT_SAMPLES,
    DEFAULT_USE_DENOISING,
    IMAGE_FORMAT_PNG,
    OVERWRITE_POLICY_OVERWRITE,
    OVERWRITE_POLICY_UNIQUE,
    RENDER_ENGINE_CYCLES,
    SHADING_MODE_RENDERED,
    VIEW_ANGLE_ACTIVE_CAMERA,
)

# ─── Render-specific value types ─────────────────────────────
FocalLength = NewType("FocalLength", float)
Aperture = NewType("Aperture", float)
FocusDistance = NewType("FocusDistance", float)
RotationDegrees = NewType("RotationDegrees", float)


# ─── FR-RND-001: Viewport capture ────────────────────────────
@dataclass(frozen=True)
class ViewportCaptureVO:
    """Viewport capture input/output VO."""

    # Input
    output_path: FilePath = field(default_factory=lambda: FilePath(""))
    max_size: MaxImageSize = field(default_factory=lambda: MaxImageSize(DEFAULT_MAX_IMAGE_SIZE))
    view_angle: str = VIEW_ANGLE_ACTIVE_CAMERA
    shading: str = SHADING_MODE_RENDERED
    show_overlays: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    focus_object: ObjectName | None = None
    image_format: ImageFormat = field(default_factory=lambda: ImageFormat(IMAGE_FORMAT_PNG))
    overwrite_policy: str = OVERWRITE_POLICY_UNIQUE
    correlation_id: RequestId = field(default_factory=lambda: RequestId(""))

    # Output
    success: SuccessFlag = field(default_factory=lambda: SuccessFlag(False))
    artifact_path: FilePath = field(default_factory=lambda: FilePath(""))
    resolved_format: ImageFormat = field(default_factory=lambda: ImageFormat(IMAGE_FORMAT_PNG))
    width: ResolutionX = field(default_factory=lambda: ResolutionX(0))
    height: ResolutionY = field(default_factory=lambda: ResolutionY(0))
    duration_ms: DurationMs = field(default_factory=lambda: DurationMs(0.0))
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── FR-RND-002: Scene render ────────────────────────────────
@dataclass(frozen=True)
class RenderSceneVO:
    """Scene render input/output VO."""

    # Input
    output_path: FilePath = field(default_factory=lambda: FilePath(""))
    resolution_x: ResolutionX = field(default_factory=lambda: ResolutionX(DEFAULT_RESOLUTION_X))
    resolution_y: ResolutionY = field(default_factory=lambda: ResolutionY(DEFAULT_RESOLUTION_Y))
    samples: RenderSamples = field(default_factory=lambda: RenderSamples(DEFAULT_SAMPLES))
    use_denoising: UseDenoising = field(default_factory=lambda: UseDenoising(DEFAULT_USE_DENOISING))
    render_engine: RenderEngine = field(default_factory=lambda: RenderEngine(RENDER_ENGINE_CYCLES))
    camera_ref: ObjectName | None = None
    overwrite_policy: str = OVERWRITE_POLICY_OVERWRITE
    background: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    correlation_id: RequestId = field(default_factory=lambda: RequestId(""))

    # Output
    success: SuccessFlag = field(default_factory=lambda: SuccessFlag(False))
    artifact_path: FilePath = field(default_factory=lambda: FilePath(""))
    render_time: RenderTime = field(default_factory=lambda: RenderTime(0.0))
    final_resolution_x: ResolutionX = field(default_factory=lambda: ResolutionX(0))
    final_resolution_y: ResolutionY = field(default_factory=lambda: ResolutionY(0))
    engine_used: RenderEngine = field(default_factory=lambda: RenderEngine(RENDER_ENGINE_CYCLES))
    denoising_applied: UseDenoising = field(default_factory=lambda: UseDenoising(False))
    task_ref: TaskUuid | None = None
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── FR-RND-003: Camera configuration ────────────────────────
@dataclass(frozen=True)
class CameraConfigVO:
    """Camera configuration input/output VO."""

    # Input
    camera_ref: ObjectName | None = None
    focal_length: FocalLength = field(default_factory=lambda: FocalLength(DEFAULT_FOCAL_LENGTH))
    sensor_fit: str = CAMERA_SENSOR_FIT_AUTO
    framing_target: ObjectName | None = None
    set_active: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    depth_of_field_enabled: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    focus_distance: FocusDistance | None = None
    focus_object: ObjectName | None = None
    aperture: Aperture = field(default_factory=lambda: Aperture(DEFAULT_APERTURE))
    create_if_missing: EnabledFlag = field(default_factory=lambda: EnabledFlag(True))
    correlation_id: RequestId = field(default_factory=lambda: RequestId(""))

    # Output
    success: SuccessFlag = field(default_factory=lambda: SuccessFlag(False))
    resolved_camera_ref: ObjectName = field(default_factory=lambda: ObjectName(""))
    final_focal_length: FocalLength = field(default_factory=lambda: FocalLength(DEFAULT_FOCAL_LENGTH))
    active_status: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    depth_of_field_applied: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── FR-RND-004: HDRI configuration ──────────────────────────
@dataclass(frozen=True)
class HdriConfigVO:
    """HDRI configuration input/output VO."""

    # Input
    hdri_path: FilePath = field(default_factory=lambda: FilePath(""))
    strength: LightStrength = field(default_factory=lambda: LightStrength(DEFAULT_HDRI_STRENGTH))
    rotation: RotationDegrees = field(default_factory=lambda: RotationDegrees(DEFAULT_HDRI_ROTATION))
    background_visible: EnabledFlag = field(default_factory=lambda: EnabledFlag(True))
    overwrite_policy: str = OVERWRITE_POLICY_OVERWRITE
    correlation_id: RequestId = field(default_factory=lambda: RequestId(""))

    # Output
    success: SuccessFlag = field(default_factory=lambda: SuccessFlag(False))
    environment_ref: ObjectName = field(default_factory=lambda: ObjectName(""))
    applied_strength: LightStrength = field(default_factory=lambda: LightStrength(0.0))
    applied_rotation: RotationDegrees = field(default_factory=lambda: RotationDegrees(0.0))
    message: Prompt = field(default_factory=lambda: Prompt(""))


# ─── Parser metrics VOs ──────────────────────────────────────
@dataclass(frozen=True)
class RenderResultMetricsVO:
    """Parsed render result metrics."""

    artifact_path: FilePath = field(default_factory=lambda: FilePath(""))
    width: ResolutionX = field(default_factory=lambda: ResolutionX(0))
    height: ResolutionY = field(default_factory=lambda: ResolutionY(0))
    render_time: RenderTime = field(default_factory=lambda: RenderTime(0.0))
    engine_used: RenderEngine = field(default_factory=lambda: RenderEngine(RENDER_ENGINE_CYCLES))
    denoising_applied: UseDenoising = field(default_factory=lambda: UseDenoising(False))


@dataclass(frozen=True)
class CameraConfigMetricsVO:
    """Parsed camera configuration metrics."""

    resolved_camera_ref: ObjectName = field(default_factory=lambda: ObjectName(""))
    final_focal_length: FocalLength = field(default_factory=lambda: FocalLength(DEFAULT_FOCAL_LENGTH))
    active_status: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))
    depth_of_field_applied: EnabledFlag = field(default_factory=lambda: EnabledFlag(False))


@dataclass(frozen=True)
class HdriConfigMetricsVO:
    """Parsed HDRI configuration metrics."""

    environment_ref: ObjectName = field(default_factory=lambda: ObjectName(""))
    applied_strength: LightStrength = field(default_factory=lambda: LightStrength(0.0))
    applied_rotation: RotationDegrees = field(default_factory=lambda: RotationDegrees(0.0))