"""Render domain contract: HDRI configuration protocol (ABC based).

Defines the protocol for configuring HDRI environment lighting.
AES Contract layer — pure ABC definitions, no implementation.

FR-RND-004: Configure HDRI Lighting
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import HdriId, LightStrength
from .taxonomy_render_request_vo import HdriSetupRequestVO


class HdriConfigProtocol(ABC):
    """Protocol for configuring HDRI environment lighting."""

    @abstractmethod
    async def configure_hdri(self, request: HdriSetupRequestVO) -> dict:
        """Set up HDRI-based environment lighting.

        FR-RND-004: Applies environment lighting from locally available HDRI asset.
        Resolves strength (0.0-10.0), rotation, and overwrite policy.
        Returns resolved environment reference and applied settings.
        """
        pass
