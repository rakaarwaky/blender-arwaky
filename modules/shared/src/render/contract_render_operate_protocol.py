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
from .taxonomy_render_vo import GetScreenshotVO, RenderVO


class RenderOperateProtocol(ABC):
    """Protocol interface for rendering, viewport capture, and camera setup."""

    @abstractmethod
    async def get_viewport_screenshot(self, request: GetScreenshotVO) -> GetScreenshotVO:
        """Capture active 3D viewport."""
        ...

    @abstractmethod
    async def setup_camera(
        self,
        location: CoordinateList,
        rotation: RotationVector,
        target: CoordinateList | None = None,
    ) -> Prompt:
        """Initialize and position camera."""
        ...

    @abstractmethod
    async def setup_render(
        self,
        engine: RenderEngine | None = None,
        samples: RenderSamples | None = None,
        resolution: CoordinateList | None = None,
        use_denoising: UseDenoising | None = None,
    ) -> Prompt:
        """Configure render engine settings."""
        ...

    @abstractmethod
    async def apply_composition(self, rule: RuleName | None = None) -> Prompt:
        """Apply compositional guides to active camera."""
        ...

    @abstractmethod
    async def render(self, request: RenderVO) -> RenderVO:
        """Execute full frame render to file."""
        ...
