"""Render domain contract: camera configuration protocol (ABC based).

Defines the protocol for configuring scene cameras.

FR-RND-003: Configure Camera
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ObjectId,
)


class CameraConfigProtocol(ABC):
    """Protocol for configuring scene cameras.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. Object feature handles positional transform only.
    """

    @abstractmethod
    async def configure_camera(
        self,
        camera_id: ObjectId | None = None,
        lens: float | None = None,
        framing_target: ObjectId | None = None,
        set_active: bool = False,
        depth_of_field: dict[str, Any] | None = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        """Configure camera optical and selection behavior.

        FR-RND-003: Creates camera if none exists (when policy allows).
        Resolves multiple cameras deterministically. Lens within valid range.
        Depth of field settings include enablement, focus distance/object, aperture.
        Framing target adjusts camera orientation preserving lens settings.
        Positional transform belongs to object feature, not here.

        Args:
            camera_id: Optional existing camera reference.
            lens: Focal length in millimeters.
            framing_target: Optional object to frame.
            set_active: Whether to designate as active scene camera.
            depth_of_field: Dict with dof settings (enable, focus_distance, aperture).
            create_if_missing: Whether to create camera if none exists.

        Returns:
            Dict with success, camera_reference, lens, active_status,
            depth_of_field_applied, and message.
        """
        ...
