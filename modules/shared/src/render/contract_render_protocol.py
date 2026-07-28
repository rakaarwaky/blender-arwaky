"""Render domain contract: operation protocols.

FR-RND-001: viewport capture protocol.
FR-RND-002: scene render protocol.
FR-RND-003: camera configuration protocol.
FR-RND-004: HDRI configuration protocol.

Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import (
    CameraConfigVO,
    HdriConfigVO,
    RenderSceneVO,
    ViewportCaptureVO,
)


class IRenderViewportCaptureProtocol(ABC):
    """Inbound contract for viewport capture capability."""

    @abstractmethod
    async def capture_viewport(self, request: ViewportCaptureVO) -> ViewportCaptureVO:
        """Capture current viewport as image artifact."""
        raise NotImplementedError


class IRenderSceneImageProtocol(ABC):
    """Inbound contract for scene render capability."""

    @abstractmethod
    async def render_scene(self, request: RenderSceneVO) -> RenderSceneVO:
        """Render scene to image artifact."""
        raise NotImplementedError


class IRenderCameraConfigProtocol(ABC):
    """Inbound contract for camera configuration capability."""

    @abstractmethod
    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO:
        """Configure camera optical and selection behavior."""
        raise NotImplementedError


class IRenderHdriConfigProtocol(ABC):
    """Inbound contract for HDRI configuration capability."""

    @abstractmethod
    async def configure_hdri(self, request: HdriConfigVO) -> HdriConfigVO:
        """Configure HDRI-based environment lighting."""
        raise NotImplementedError