"""Render taxonomy constants.

Stable domain constants for render, capture, camera, and HDRI behavior.
"""

from typing import Final

# ─── Viewport capture ────────────────────────────────────────
VIEW_ANGLE_PERSPECTIVE: Final[str] = "perspective"
VIEW_ANGLE_ORTHOGRAPHIC: Final[str] = "orthographic"
VIEW_ANGLE_ACTIVE_CAMERA: Final[str] = "active_camera"

VALID_VIEW_ANGLES: Final[frozenset[str]] = frozenset(
    (
        VIEW_ANGLE_PERSPECTIVE,
        VIEW_ANGLE_ORTHOGRAPHIC,
        VIEW_ANGLE_ACTIVE_CAMERA,
    )
)

SHADING_MODE_WIREFRAME: Final[str] = "wireframe"
SHADING_MODE_SOLID: Final[str] = "solid"
SHADING_MODE_MATERIAL_PREVIEW: Final[str] = "material_preview"
SHADING_MODE_RENDERED: Final[str] = "rendered"

VALID_SHADING_MODES: Final[frozenset[str]] = frozenset(
    (
        SHADING_MODE_WIREFRAME,
        SHADING_MODE_SOLID,
        SHADING_MODE_MATERIAL_PREVIEW,
        SHADING_MODE_RENDERED,
    )
)

IMAGE_FORMAT_PNG: Final[str] = "PNG"
IMAGE_FORMAT_JPEG: Final[str] = "JPEG"
IMAGE_FORMAT_OPEN_EXR: Final[str] = "OPEN_EXR"

VALID_IMAGE_FORMATS: Final[frozenset[str]] = frozenset(
    (
        IMAGE_FORMAT_PNG,
        IMAGE_FORMAT_JPEG,
        IMAGE_FORMAT_OPEN_EXR,
    )
)

DEFAULT_MAX_IMAGE_SIZE: Final[int] = 800

# ─── Output policies ─────────────────────────────────────────
OVERWRITE_POLICY_OVERWRITE: Final[str] = "overwrite"
OVERWRITE_POLICY_REJECT: Final[str] = "reject"
OVERWRITE_POLICY_UNIQUE: Final[str] = "unique"

VALID_OVERWRITE_POLICIES: Final[frozenset[str]] = frozenset(
    (
        OVERWRITE_POLICY_OVERWRITE,
        OVERWRITE_POLICY_REJECT,
        OVERWRITE_POLICY_UNIQUE,
    )
)

# ─── Render defaults ─────────────────────────────────────────
RENDER_ENGINE_CYCLES: Final[str] = "CYCLES"
RENDER_ENGINE_EEVEE: Final[str] = "BLENDER_EEVEE"

VALID_RENDER_ENGINES: Final[frozenset[str]] = frozenset(
    (
        RENDER_ENGINE_CYCLES,
        RENDER_ENGINE_EEVEE,
    )
)

DEFAULT_RESOLUTION_X: Final[int] = 1920
DEFAULT_RESOLUTION_Y: Final[int] = 1080
DEFAULT_SAMPLES: Final[int] = 128
DEFAULT_USE_DENOISING: Final[bool] = True

MIN_RESOLUTION: Final[int] = 1
MAX_RESOLUTION: Final[int] = 8192
MIN_SAMPLES: Final[int] = 1
MAX_SAMPLES: Final[int] = 32768

# ─── Camera defaults ─────────────────────────────────────────
DEFAULT_FOCAL_LENGTH: Final[float] = 50.0
MIN_FOCAL_LENGTH: Final[float] = 10.0
MAX_FOCAL_LENGTH: Final[float] = 300.0

DEFAULT_APERTURE: Final[float] = 5.6
DEFAULT_FOCUS_DISTANCE: Final[float] = 10.0

CAMERA_SENSOR_FIT_AUTO: Final[str] = "AUTO"
CAMERA_SENSOR_FIT_HORIZONTAL: Final[str] = "HORIZONTAL"
CAMERA_SENSOR_FIT_VERTICAL: Final[str] = "VERTICAL"

VALID_SENSOR_FITS: Final[frozenset[str]] = frozenset(
    (
        CAMERA_SENSOR_FIT_AUTO,
        CAMERA_SENSOR_FIT_HORIZONTAL,
        CAMERA_SENSOR_FIT_VERTICAL,
    )
)

# ─── HDRI defaults ──────────────────────────────────────────
DEFAULT_HDRI_STRENGTH: Final[float] = 1.0
MIN_HDRI_STRENGTH: Final[float] = 0.0
MAX_HDRI_STRENGTH: Final[float] = 10.0

DEFAULT_HDRI_ROTATION: Final[float] = 0.0

VALID_HDRI_STRENGTH_RANGE: Final[tuple[float, float]] = (MIN_HDRI_STRENGTH, MAX_HDRI_STRENGTH)
