"""Render domain shared contracts, taxonomy, and utilities."""

from __future__ import annotations

# ─── Taxonomy Module Barrel Exports ──────────────────────
from . import (
    taxonomy_render_constant,
    taxonomy_render_error,
    taxonomy_render_event,
    taxonomy_render_vo,
)

from .contract_render_aggregate import IRenderAggregate
from .contract_render_camera_config_protocol import IRenderCameraConfigProtocol
from .contract_render_hdri_config_protocol import IRenderHdriConfigProtocol
from .contract_render_scene_image_protocol import IRenderSceneImageProtocol
from .contract_render_viewport_capture_protocol import IRenderViewportCaptureProtocol

from .taxonomy_render_constant import (
    CAMERA_SENSOR_FIT_AUTO,
    CAMERA_SENSOR_FIT_HORIZONTAL,
    CAMERA_SENSOR_FIT_VERTICAL,
    DEFAULT_APERTURE,
    DEFAULT_FOCAL_LENGTH,
    DEFAULT_FOCUS_DISTANCE,
    DEFAULT_HDRI_ROTATION,
    DEFAULT_HDRI_STRENGTH,
    DEFAULT_MAX_IMAGE_SIZE,
    DEFAULT_RESOLUTION_X,
    DEFAULT_RESOLUTION_Y,
    DEFAULT_SAMPLES,
    DEFAULT_USE_DENOISING,
    IMAGE_FORMAT_JPEG,
    IMAGE_FORMAT_OPEN_EXR,
    IMAGE_FORMAT_PNG,
    MAX_FOCAL_LENGTH,
    MAX_HDRI_STRENGTH,
    MAX_RESOLUTION,
    MAX_SAMPLES,
    MIN_FOCAL_LENGTH,
    MIN_HDRI_STRENGTH,
    MIN_RESOLUTION,
    MIN_SAMPLES,
    OVERWRITE_POLICY_OVERWRITE,
    OVERWRITE_POLICY_REJECT,
    OVERWRITE_POLICY_UNIQUE,
    RENDER_ENGINE_CYCLES,
    RENDER_ENGINE_EEVEE,
    SHADING_MODE_MATERIAL_PREVIEW,
    SHADING_MODE_RENDERED,
    SHADING_MODE_SOLID,
    SHADING_MODE_WIREFRAME,
    VALID_IMAGE_FORMATS,
    VALID_OVERWRITE_POLICIES,
    VALID_RENDER_ENGINES,
    VALID_SENSOR_FITS,
    VALID_SHADING_MODES,
    VALID_VIEW_ANGLES,
    VIEW_ANGLE_ACTIVE_CAMERA,
    VIEW_ANGLE_ORTHOGRAPHIC,
    VIEW_ANGLE_PERSPECTIVE,
)

from .taxonomy_render_error import RenderError, RenderErrorCategory

from .taxonomy_render_event import (
    CameraConfiguredEvent,
    HdriLightingConfiguredEvent,
    RenderSubmittedToBackgroundEvent,
    SceneRenderCompletedEvent,
    SceneRenderFailedEvent,
    ViewportCapturedEvent,
)

from .taxonomy_render_vo import (
    Aperture,
    CameraConfigMetricsVO,
    CameraConfigVO,
    FocalLength,
    FocusDistance,
    HdriConfigMetricsVO,
    HdriConfigVO,
    RenderResultMetricsVO,
    RenderSceneVO,
    RotationDegrees,
    ViewportCaptureVO,
)

__all__ = [
    # Contracts
    "IRenderAggregate",
    "IRenderCameraConfigProtocol",
    "IRenderHdriConfigProtocol",
    "IRenderSceneImageProtocol",
    "IRenderViewportCaptureProtocol",

    # Constants
    "CAMERA_SENSOR_FIT_AUTO",
    "CAMERA_SENSOR_FIT_HORIZONTAL",
    "CAMERA_SENSOR_FIT_VERTICAL",
    "DEFAULT_APERTURE",
    "DEFAULT_FOCAL_LENGTH",
    "DEFAULT_FOCUS_DISTANCE",
    "DEFAULT_HDRI_ROTATION",
    "DEFAULT_HDRI_STRENGTH",
    "DEFAULT_MAX_IMAGE_SIZE",
    "DEFAULT_RESOLUTION_X",
    "DEFAULT_RESOLUTION_Y",
    "DEFAULT_SAMPLES",
    "DEFAULT_USE_DENOISING",
    "IMAGE_FORMAT_JPEG",
    "IMAGE_FORMAT_OPEN_EXR",
    "IMAGE_FORMAT_PNG",
    "MAX_FOCAL_LENGTH",
    "MAX_HDRI_STRENGTH",
    "MAX_RESOLUTION",
    "MAX_SAMPLES",
    "MIN_FOCAL_LENGTH",
    "MIN_HDRI_STRENGTH",
    "MIN_RESOLUTION",
    "MIN_SAMPLES",
    "OVERWRITE_POLICY_OVERWRITE",
    "OVERWRITE_POLICY_REJECT",
    "OVERWRITE_POLICY_UNIQUE",
    "RENDER_ENGINE_CYCLES",
    "RENDER_ENGINE_EEVEE",
    "SHADING_MODE_MATERIAL_PREVIEW",
    "SHADING_MODE_RENDERED",
    "SHADING_MODE_SOLID",
    "SHADING_MODE_WIREFRAME",
    "VALID_IMAGE_FORMATS",
    "VALID_OVERWRITE_POLICIES",
    "VALID_RENDER_ENGINES",
    "VALID_SENSOR_FITS",
    "VALID_SHADING_MODES",
    "VALID_VIEW_ANGLES",
    "VIEW_ANGLE_ACTIVE_CAMERA",
    "VIEW_ANGLE_ORTHOGRAPHIC",
    "VIEW_ANGLE_PERSPECTIVE",

    # Errors
    "RenderError",
    "RenderErrorCategory",

    # Events
    "CameraConfiguredEvent",
    "HdriLightingConfiguredEvent",
    "RenderSubmittedToBackgroundEvent",
    "SceneRenderCompletedEvent",
    "SceneRenderFailedEvent",
    "ViewportCapturedEvent",

    # VOs
    "Aperture",
    "CameraConfigMetricsVO",
    "CameraConfigVO",
    "FocalLength",
    "FocusDistance",
    "HdriConfigMetricsVO",
    "HdriConfigVO",
    "RenderResultMetricsVO",
    "RenderSceneVO",
    "RotationDegrees",
    "ViewportCaptureVO",
]
