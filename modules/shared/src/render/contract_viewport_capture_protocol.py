"""Render domain contract: viewport screenshot capture protocol (ABC based).

Defines the protocol for capturing the viewport as an image artifact.

FR-RND-001: Capture Viewport Screenshot
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    ImageFormat,
    MaxImageSize,
    ObjectId,
)


class ViewportCaptureProtocol(ABC):
    """Protocol for capturing viewport screenshots.

    FR-RND-001: Captures viewport as image artifact at validated output location.
    Returns file reference with capture metadata (dimensions, format, duration).
    """

    @abstractmethod
    async def capture_viewport(
        self,
        max_size: MaxImageSize | None = None,
        view_angle: str = "perspective",
        shading_mode: str = "rendered",
        overlay_visible: bool = True,
        focus_object_id: ObjectId | None = None,
        image_format: ImageFormat | None = None,
        output_path: FilePath | None = None,
        overwrite_policy: str = "overwrite",
    ) -> dict[str, Any]:
        """Capture current viewport as image artifact.

        FR-RND-001: Output location validated through security policy.
        View angle must be perspective/orthographic/active_camera.
        Shading mode must be wireframe/solid/material_preview/rendered.
        Max size enforced while preserving aspect ratio.
        Result returns file reference with metadata.

        Args:
            max_size: Maximum image dimension limit.
            view_angle: perspective, orthographic, or active_camera.
            shading_mode: wireframe, solid, material_preview, or rendered.
            overlay_visible: Whether to show viewport overlays.
            focus_object_id: Optional object to focus on during capture.
            image_format: Output image format (png, jpg, etc.).
            output_path: Optional output file path.
            overwrite_policy: overwrite/reject/unique for existing files.

        Returns:
            Dict with success, file_path, image_format, width, height,
            shading_mode, duration, and message.
        """
        ...
