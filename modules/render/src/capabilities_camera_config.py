"""Capability: Camera configuration (FR-RND-003).

Implements CameraConfigProtocol for configuring scene cameras.
Returns resolved camera reference and final settings.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from modules.shared.src.render.contract_camera_config_protocol import CameraConfigProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectId

logger = logging.getLogger("BlenderMCPServer")


class CameraConfigCapability(CameraConfigProtocol):
    """Camera configuration capability.

    FR-RND-003: Configures camera optical properties including lens, framing,
    active designation, and depth of field. Returns resolved camera reference
    and final settings. Object feature handles positional transform only.
    """

    def __init__(
        self,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.security_validator = security_validator
        self.config_getter = config_getter

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
        # Validate lens range if provided
        if lens is not None:
            valid_range = (10.0, 300.0)  # Typical Blender range
            if lens < valid_range[0] or lens > valid_range[1]:
                return {
                    "success": False,
                    "camera_reference": None,
                    "lens": lens,
                    "active_status": False,
                    "depth_of_field_applied": False,
                    "message": f"Lens {lens}mm out of range ({valid_range[0]}-{valid_range[1]})",
                    "error": "invalid_parameter",
                }

        # Build camera configuration command
        config_command = self._build_camera_command(
            camera_id, lens, framing_target, set_active, depth_of_field, create_if_missing
        )

        # Execute through gateway
        try:
            result = await self.gateway_client.execute_command(config_command)
            return {
                "success": True,
                "camera_reference": result.get("camera_id"),
                "lens": lens or result.get("current_lens", 50.0),
                "active_status": result.get("is_active", False),
                "depth_of_field_applied": result.get("dof_enabled", False),
                "message": f"Camera {str(camera_id or 'created')} configured successfully",
            }
        except Exception as e:
            logger.error("Camera configuration failed: %s", e)
            return {
                "success": False,
                "camera_reference": None,
                "lens": lens,
                "active_status": False,
                "depth_of_field_applied": False,
                "message": f"Camera configuration failed: {e}",
                "error": str(e),
            }

    def _build_camera_command(
        self,
        camera_id: ObjectId | None,
        lens: float | None,
        framing_target: ObjectId | None,
        set_active: bool,
        depth_of_field: dict[str, Any] | None,
        create_if_missing: bool,
    ) -> dict[str, Any]:
        """Build camera config command for gateway transport."""
        command = {
            "type": "camera_configure",
            "create_if_missing": create_if_missing,
            "set_active": set_active,
        }

        if camera_id:
            command["camera_id"] = str(camera_id)

        if lens is not None:
            command["lens"] = lens

        if framing_target:
            command["framing_target"] = str(framing_target)

        if depth_of_field:
            command["depth_of_field"] = depth_of_field

        return command
