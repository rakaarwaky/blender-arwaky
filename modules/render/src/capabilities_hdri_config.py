"""Capability: HDRI lighting configuration (FR-RND-004).

Implements HdriConfigProtocol for configuring HDRI environment lighting.
Never downloads HDRI itself — uses asset feature to get HDRI file.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.render.contract_hdri_config_protocol import HdriConfigProtocol
from modules.shared.src.common.taxonomy_core_vo import FilePath

logger = logging.getLogger("BlenderMCPServer")


class HdriConfigCapability(HdriConfigProtocol):
    """HDRI lighting configuration capability.

    FR-RND-004: Applies HDRI-based environment lighting using locally available
    HDRI file acquired through asset feature. Resolves strength (0-10), rotation,
    overwrite policy, and background visibility. Never downloads HDRI itself.
    """

    def __init__(
        self,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        asset_feature: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            asset_feature: Asset feature for HDRI file acquisition.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.security_validator = security_validator
        self.asset_feature = asset_feature
        self.config_getter = config_getter

    async def configure_hdri(
        self,
        hdri_file_path: FilePath,
        strength: float = 1.0,
        rotation: float = 0.0,
        background_visible: bool = True,
        overwrite_policy: str = "replace",
    ) -> dict[str, Any]:
        """Set up HDRI-based environment lighting.

        FR-RND-004: HDRI file must be locally available (acquired via asset feature).
        Local file validated through security policy. Strength in valid range (0-10).
        Rotation normalized. Existing environment follows overwrite policy.
        Environment applies to scene world; world created if missing (when allowed).
        Background visibility controls HDRI appearance vs lighting-only contribution.

        Args:
            hdri_file_path: Path to local HDRI file (from asset feature).
            strength: Environment strength (0.0-10.0 range).
            rotation: HDRI rotation in degrees.
            background_visible: Whether HDRI appears as visible background.
            overwrite_policy: replace/update/reject for existing environment.

        Returns:
            Dict with success, environment_reference, strength, rotation,
            and message.
        """
        # Validate strength range
        if strength < 0.0 or strength > 10.0:
            return {
                "success": False,
                "environment_reference": None,
                "strength": strength,
                "rotation": rotation,
                "message": f"HDRI strength {strength} out of range (0.0-10.0)",
                "error": "invalid_parameter",
            }

        # Normalize rotation to [0, 360)
        rotation = rotation % 360.0

        # Validate HDRI file path through security policy
        if self.security_validator:
            try:
                await self.security_validator.validate_path(hdri_file_path, "read")
            except Exception as e:
                logger.warning("HDRI path validation failed: %s", e)
                return {
                    "success": False,
                    "environment_reference": None,
                    "strength": strength,
                    "rotation": rotation,
                    "message": f"HDRI path validation failed: {e}",
                    "error": "security_violation",
                }

        # Check if HDRI file exists locally
        import os
        if not os.path.exists(hdri_file_path):
            # Try to acquire through asset feature
            if self.asset_feature:
                try:
                    logger.info("HDRI file not found, attempting acquisition via asset feature")
                    download_result = await self.asset_feature.download_to_cache(
                        provider="polyhaven",  # Default provider
                        asset_id=hdri_file_path,  # Use path as ID for lookup
                        asset_type="hdri",
                        cache_dir=FilePath(""),
                    )
                    if not download_result.get("success"):
                        return {
                            "success": False,
                            "environment_reference": None,
                            "strength": strength,
                            "rotation": rotation,
                            "message": f"HDRI acquisition failed: {download_result.get('message', 'unknown error')}",
                            "error": "asset_not_found",
                        }
                    hdri_file_path = FilePath(download_result.get("file_path", ""))
                except Exception as e:
                    logger.error("HDRI acquisition failed: %s", e)
                    return {
                        "success": False,
                        "environment_reference": None,
                        "strength": strength,
                        "rotation": rotation,
                        "message": f"HDRI acquisition failed: {e}",
                        "error": "asset_not_found",
                    }

            # Still not found after attempt
            if not os.path.exists(hdri_file_path):
                return {
                    "success": False,
                    "environment_reference": None,
                    "strength": strength,
                    "rotation": rotation,
                    "message": f"HDRI file not found: {hdri_file_path}",
                    "error": "asset_not_found",
                }

        # Build HDRI configuration command
        hdri_command = self._build_hdri_command(
            hdri_file_path, strength, rotation, background_visible, overwrite_policy
        )

        # Execute through gateway
        try:
            result = await self.gateway_client.execute_command(hdri_command)
            return {
                "success": True,
                "environment_reference": result.get("environment_name"),
                "strength": strength,
                "rotation": rotation,
                "message": f"HDRI lighting configured with {hdri_file_path}",
            }
        except Exception as e:
            logger.error("HDRI configuration failed: %s", e)
            return {
                "success": False,
                "environment_reference": None,
                "strength": strength,
                "rotation": rotation,
                "message": f"HDRI configuration failed: {e}",
                "error": str(e),
            }

    def _build_hdri_command(
        self,
        hdri_path: str,
        strength: float,
        rotation: float,
        background_visible: bool,
        overwrite_policy: str,
    ) -> dict[str, Any]:
        """Build HDRI config command for gateway transport."""
        return {
            "type": "hdri_configure",
            "hdri_path": hdri_path,
            "strength": strength,
            "rotation": rotation,
            "background_visible": background_visible,
            "overwrite_policy": overwrite_policy,
        }
