"""Render utility: result parsers.

Stateless parsers for Blender execution output.
"""

from __future__ import annotations

import json
import logging

from ..common.taxonomy_core_vo import (
    EnabledFlag,
    FilePath,
    ImageFormat,
    LightStrength,
    ObjectName,
    Prompt,
    RenderEngine,
    RenderTime,
    ResolutionX,
    ResolutionY,
    UseDenoising,
)
from .taxonomy_render_constant import (
    DEFAULT_FOCAL_LENGTH,
    IMAGE_FORMAT_PNG,
    RENDER_ENGINE_CYCLES,
)
from .taxonomy_render_vo import (
    CameraConfigMetricsVO,
    FocalLength,
    HdriConfigMetricsVO,
    RenderResultMetricsVO,
    RotationDegrees,
)

logger = logging.getLogger("BlenderMCPServer")


def parse_artifact_result(raw: Prompt | None) -> tuple[FilePath, ResolutionX, ResolutionY, ImageFormat]:
    """Parse generic artifact result."""
    if raw is None:
        return (
            FilePath(""),
            ResolutionX(0),
            ResolutionY(0),
            ImageFormat(IMAGE_FORMAT_PNG),
        )

    text = str(raw)

    try:
        data = json.loads(text)
    except Exception as exc:
        logger.warning("Failed to parse artifact result: %s", exc)
        return (
            FilePath(""),
            ResolutionX(0),
            ResolutionY(0),
            ImageFormat(IMAGE_FORMAT_PNG),
        )

    if not isinstance(data, dict):
        return (
            FilePath(""),
            ResolutionX(0),
            ResolutionY(0),
            ImageFormat(IMAGE_FORMAT_PNG),
        )

    return (
        FilePath(str(data.get("artifact_path", ""))),
        ResolutionX(int(data.get("width", 0))),
        ResolutionY(int(data.get("height", 0))),
        ImageFormat(str(data.get("format", IMAGE_FORMAT_PNG))),
    )


def parse_render_result(raw: Prompt | None) -> RenderResultMetricsVO:
    """Parse render result metrics."""
    if raw is None:
        return RenderResultMetricsVO()

    text = str(raw)

    try:
        data = json.loads(text)
    except Exception as exc:
        logger.warning("Failed to parse render result: %s", exc)
        return RenderResultMetricsVO()

    if not isinstance(data, dict):
        return RenderResultMetricsVO()

    return RenderResultMetricsVO(
        artifact_path=FilePath(str(data.get("artifact_path", ""))),
        width=ResolutionX(int(data.get("width", 0))),
        height=ResolutionY(int(data.get("height", 0))),
        render_time=RenderTime(float(data.get("render_time", 0.0))),
        engine_used=RenderEngine(str(data.get("engine_used", RENDER_ENGINE_CYCLES))),
        denoising_applied=UseDenoising(bool(data.get("denoising_applied", False))),
    )


def parse_camera_config_result(raw: Prompt | None) -> CameraConfigMetricsVO:
    """Parse camera configuration result."""
    if raw is None:
        return CameraConfigMetricsVO()

    text = str(raw)

    try:
        data = json.loads(text)
    except Exception as exc:
        logger.warning("Failed to parse camera config result: %s", exc)
        return CameraConfigMetricsVO()

    if not isinstance(data, dict):
        return CameraConfigMetricsVO()

    return CameraConfigMetricsVO(
        resolved_camera_ref=ObjectName(str(data.get("camera_reference", ""))),
        final_focal_length=FocalLength(float(data.get("final_focal_length", DEFAULT_FOCAL_LENGTH))),
        active_status=EnabledFlag(bool(data.get("active_status", False))),
        depth_of_field_applied=EnabledFlag(bool(data.get("depth_of_field_applied", False))),
    )


def parse_hdri_config_result(raw: Prompt | None) -> HdriConfigMetricsVO:
    """Parse HDRI configuration result."""
    if raw is None:
        return HdriConfigMetricsVO()

    text = str(raw)

    try:
        data = json.loads(text)
    except Exception as exc:
        logger.warning("Failed to parse HDRI config result: %s", exc)
        return HdriConfigMetricsVO()

    if not isinstance(data, dict):
        return HdriConfigMetricsVO()

    return HdriConfigMetricsVO(
        environment_ref=ObjectName(str(data.get("environment_ref", ""))),
        applied_strength=LightStrength(float(data.get("applied_strength", 0.0))),
        applied_rotation=RotationDegrees(float(data.get("applied_rotation", 0.0))),
    )