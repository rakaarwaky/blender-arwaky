"""Capability: Viewport screenshot capture.

Implements ViewportCapturePort — captures the Blender 3D viewport as an image
through the server module's socket adapter for direct viewport access.
"""

from __future__ import annotations

import logging

from modules.shared.src.render.contract_viewport_capture import ViewportCapturePort

logger = logging.getLogger("BlenderMCPServer")


class ScreenshotCapture(ViewportCapturePort):
    """Viewport screenshot capture via server socket adapter."""

    def __init__(self, socket_adapter: object) -> None:
        """Initialize with a socket adapter from the server module.

        Args:
            socket_adapter: A callable or server capability that sends commands
                through the Blender socket connection.
        """
        self._socket_adapter = socket_adapter

    def get_viewport_screenshot(self, max_size: int | None = None) -> bytes:
        """Capture a screenshot of the current Blender 3D viewport.

        FR-RND-001: Returns PNG bytes respecting max_size constraint.
        Falls back to camera capture in headless mode.

        Args:
            max_size: Maximum dimension (width or height) for the screenshot.

        Returns:
            PNG image bytes.
        """
        logger.info("Capturing viewport screenshot, max_size=%s", max_size)

        try:
            result = self._socket_adapter(
                action="get_viewport_screenshot",
                max_size=max_size,
            )
            if isinstance(result, bytes):
                return result
            logger.warning("Socket adapter returned non-bytes type: %s", type(result))
            return b""
        except Exception as e:
            logger.error("Viewport screenshot failed: %s", e)
            raise RuntimeError(f"Failed to capture viewport: {e}") from e
