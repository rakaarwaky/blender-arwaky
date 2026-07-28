"""Render domain contract: viewport screenshot capture aggregate (ABC).

Aggregates all viewport capture operations into a single facade that the Agent
layer consumes. Surface layer depends on this aggregate.

FR-RND-001: Capture Viewport Screenshot
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import GetScreenshotVO


class ViewportCaptureAggregate(ABC):
    """Aggregate facade for viewport screenshot capture operations.

    FR-RND-001: Captures the current viewport as an image artifact at a
    validated output location. Returns file reference with capture metadata.
    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def capture_viewport(self, request: GetScreenshotVO) -> GetScreenshotVO:
        """FR-RND-001: Capture current viewport as image artifact.

        Output location validated through security policy. View angle must be
        perspective/orthographic/active_camera. Shading mode must be
        wireframe/solid/material_preview/rendered. Max size enforced while
        preserving aspect ratio. Result returns file reference with metadata.

        Args:
            request: Screenshot capture request with max_size, view_angle,
                     shading_mode, overlay_visibility, and focus_object.

        Returns:
            GetScreenshotVO with success, image_path, dimensions, format,
            duration_ms, and message.
        """
        ...
