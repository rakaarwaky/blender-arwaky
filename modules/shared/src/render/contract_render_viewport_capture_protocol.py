"""Render domain — FR-RND-001: Capture viewport screenshot."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import ViewportCaptureVO


class IRenderViewportCaptureProtocol(ABC):
    @abstractmethod
    async def capture_viewport(self, request: ViewportCaptureVO) -> ViewportCaptureVO: ...
