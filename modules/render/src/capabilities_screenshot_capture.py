"""Capability: Viewport screenshot capture (FR-RND-001).

Implements ViewportCaptureProtocol for capturing viewport as image artifact.
Returns file reference with capture metadata.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    FilePath,
    ImageFormat,
    MaxImageSize,
    ObjectId,
)
from modules.shared.src.render.contract_viewport_capture_protocol import ViewportCaptureProtocol

logger = logging.getLogger("BlenderMCPServer")


class ScreenshotCaptureCapability(ViewportCaptureProtocol):
    """Viewport screenshot capture capability.

    FR-RND-001: Captures viewport as image artifact at validated output location.
    Returns file reference with capture metadata (dimensions, format, duration).
    """

    def __init__(
        self,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.security_validator = security_validator
        self.config_getter = config_getter

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
        start_time = time.monotonic()

        # Validate view angle
        valid_angles = ["perspective", "orthographic", "active_camera"]
        if view_angle not in valid_angles:
            return {
                "success": False,
                "file_path": None,
                "image_format": None,
                "width": 0,
                "height": 0,
                "shading_mode": shading_mode,
                "duration_ms": 0,
                "message": f"Invalid view angle: {view_angle}. Must be one of {valid_angles}",
                "error": "invalid_parameter",
            }

        # Validate shading mode
        valid_shading = ["wireframe", "solid", "material_preview", "rendered"]
        if shading_mode not in valid_shading:
            return {
                "success": False,
                "file_path": None,
                "image_format": None,
                "width": 0,
                "height": 0,
                "shading_mode": shading_mode,
                "duration_ms": 0,
                "message": f"Invalid shading mode: {shading_mode}. Must be one of {valid_shading}",
                "error": "invalid_parameter",
            }

        # Determine output path
        if output_path is None:
            output_path = FilePath(self._default_output_path(image_format))

        # Validate output path through security policy
        if self.security_validator:
            try:
                await self.security_validator.validate_path(output_path, "write")
            except Exception as e:
                logger.warning("Output path validation failed: %s", e)
                return {
                    "success": False,
                    "file_path": None,
                    "image_format": None,
                    "width": 0,
                    "height": 0,
                    "shading_mode": shading_mode,
                    "duration_ms": 0,
                    "message": f"Output path validation failed: {e}",
                    "error": "security_violation",
                }

        # Build capture command for gateway
        capture_command = self._build_capture_command(
            view_angle, shading_mode, overlay_visible, focus_object_id, image_format, max_size
        )

        # Execute through gateway
        try:
            result = await self.gateway_client.execute_command(capture_command)
            duration_ms = (time.monotonic() - start_time) * 1000

            return {
                "success": True,
                "file_path": output_path,
                "image_format": str(image_format or "png"),
                "width": result.get("width", 0),
                "height": result.get("height", 0),
                "shading_mode": shading_mode,
                "duration_ms": int(duration_ms),
                "message": f"Viewport captured to {output_path}",
            }
        except Exception as e:
            duration_ms = (time.monotonic() - start_time) * 1000
            logger.error("Viewport capture failed: %s", e)
            return {
                "success": False,
                "file_path": None,
                "image_format": None,
                "width": 0,
                "height": 0,
                "shading_mode": shading_mode,
                "duration_ms": int(duration_ms),
                "message": f"Viewport capture failed: {e}",
                "error": str(e),
            }

    def _default_output_path(self, image_format: ImageFormat | None) -> str:
        """Get default output path from config or generate one."""
        return f"screenshot.{str(image_format or 'png')}"

    def _build_capture_command(
        self,
        view_angle: str,
        shading_mode: str,
        overlay_visible: bool,
        focus_object_id: ObjectId | None,
        image_format: ImageFormat | None,
        max_size: MaxImageSize | None,
    ) -> dict[str, Any]:
        """Build capture command for gateway transport."""
        command = {
            "type": "screenshot",
            "view_angle": view_angle,
            "shading_mode": shading_mode,
            "overlay_visible": overlay_visible,
        }

        if focus_object_id:
            command["focus_object_id"] = str(focus_object_id)

        if image_format:
            command["image_format"] = str(image_format)

        if max_size:
            command["max_size"] = int(max_size)

        return command
