"""Render domain contract: camera configuration protocol (ABC based).

Defines the protocol for configuring scene cameras.
AES Contract layer — pure ABC definitions, no implementation.

FR-RND-003: Configure Camera
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_request_vo import CameraConfigResultVO, CameraSetupRequestVO


class CameraConfigProtocol(ABC):
    """Protocol for configuring scene cameras."""

    @abstractmethod
    async def configure_camera(self, request: CameraSetupRequestVO) -> CameraConfigResultVO:
        """Position and configure a scene camera.

        FR-RND-003: Creates camera if none exists (when policy allows).
        Resolves multiple cameras deterministically.
        Returns resolved camera reference and final settings.
        """
        pass
