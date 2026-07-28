"""Render domain contract: camera configuration aggregate (ABC).

Aggregates all camera configuration operations into a single facade that the Agent
layer consumes. Surface layer depends on this aggregate.

FR-RND-003: Configure Camera
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import CameraConfigVO


class CameraConfigAggregate(ABC):
    """Aggregate facade for camera configuration operations.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO:
        """FR-RND-003: Configure camera optical and selection behavior.

        Creates camera if none exists (when policy allows). Resolves multiple
        cameras deterministically. Lens within valid range. Depth of field
        settings include enablement, focus distance/object, aperture. Framing
        target adjusts camera orientation preserving lens settings. Positional
        transform belongs to object feature, not here.

        Args:
            request: Camera config with camera_id, lens, framing_target,
                     set_active, depth_of_field, and create_if_missing.

        Returns:
            CameraConfigVO with success, camera_name, final_settings,
            and message.
        """
        ...
