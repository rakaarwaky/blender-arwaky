"""Render domain — FR-RND-003: Configure camera."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import CameraConfigVO


class IRenderCameraConfigProtocol(ABC):
    @abstractmethod
    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO: ...
