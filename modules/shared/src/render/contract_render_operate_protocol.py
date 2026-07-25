"""Render domain contract: render operations protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import (
    CoordinateList,
    Prompt,
    RenderEngine,
    RenderSamples,
    RotationVector,
    RuleName,
    UseDenoising,
)
from .taxonomy_render_request_vo import (
    GetScreenshotRequestVO,
    RenderRequestVO,
    RenderResponseVO,
    ScreenshotResponseVO,
)


class RenderOperateProtocol(ABC):
    """Protocol interface for rendering, viewport capture, and camera setup."""

    @abstractmethod
    async def get_viewport_screenshot(
        self, request: GetScreenshotRequestVO
    ) -> ScreenshotResponseVO:
        """Capture active 3D viewport."""
        pass

    @abstractmethod
    async def setup_camera(
        self,
        location: CoordinateList,
        rotation: RotationVector,
        target: CoordinateList | None = None,
    ) -> Prompt:
        """Initialize and position camera."""
        pass

    @abstractmethod
    async def setup_render(
        self,
        engine: RenderEngine | None = None,
        samples: RenderSamples | None = None,
        resolution: CoordinateList | None = None,
        use_denoising: UseDenoising | None = None,
    ) -> Prompt:
        """Configure render engine settings."""
        pass

    @abstractmethod
    async def apply_composition(
        self, rule: RuleName | None = None
    ) -> Prompt:
        """Apply compositional guides to active camera."""
        pass

    @abstractmethod
    async def render(
        self, request: RenderRequestVO
    ) -> RenderResponseVO:
        """Execute full frame render to file."""
        pass
