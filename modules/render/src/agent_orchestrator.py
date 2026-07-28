"""Agent: Render feature orchestrator.

Coordinates viewport capture, image rendering, camera setup, and HDRI
configuration through the render capability protocols.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.render.contract_camera_config_protocol import CameraConfigProtocol
from modules.shared.src.render.contract_hdri_config_protocol import HdriConfigProtocol
from modules.shared.src.render.contract_render_aggregate import (
    CameraConfigAggregate,
    HdriConfigAggregate,
    RenderOperateAggregate,
    ViewportCaptureAggregate,
)
from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    GetScreenshotVO,
    RenderVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderOrchestrator:
    """Orchestrates render operations via capability protocols."""

    def __init__(
        self,
        executor: RenderOperateProtocol,
        camera_config: CameraConfigProtocol | None = None,
        hdri_config: HdriConfigProtocol | None = None,
    ) -> None:
        self._executor = executor
        self._camera_config = camera_config
        self._hdri_config = hdri_config

    async def get_screenshot(self, request: GetScreenshotVO) -> GetScreenshotVO:
        return await self._executor.get_viewport_screenshot(request)

    async def render(self, request: RenderVO) -> RenderVO:
        return await self._executor.render(request)

    # ─── Camera Configuration (FR-RND-003) ──────────────────────────────

    async def configure_camera(
        self,
        camera_id: str | None = None,
        lens: float | None = None,
        framing_target: str | None = None,
        set_active: bool = False,
        depth_of_field: dict[str, Any] | None = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        """FR-RND-003: Configure camera optical and selection behavior.

        Delegates to CameraConfigCapability when available.
        """
        if self._camera_config is None:
            return {
                "success": False,
                "message": "CameraConfigCapability not available",
            }
        return await self._camera_config.configure_camera(
            camera_id=camera_id,
            lens=lens,
            framing_target=framing_target,
            set_active=set_active,
            depth_of_field=depth_of_field,
            create_if_missing=create_if_missing,
        )

    # ─── HDRI Configuration (FR-RND-004) ────────────────────────────────

    async def configure_hdri(
        self,
        hdri_file_path: str,
        strength: float = 1.0,
        rotation: float = 0.0,
        background_visible: bool = True,
        overwrite_policy: str = "replace",
    ) -> dict[str, Any]:
        """FR-RND-004: Set up HDRI-based environment lighting.

        Delegates to HdriConfigCapability when available.
        """
        if self._hdri_config is None:
            return {
                "success": False,
                "message": "HdriConfigCapability not available",
            }
        return await self._hdri_config.configure_hdri(
            hdri_file_path=hdri_file_path,
            strength=strength,
            rotation=rotation,
            background_visible=background_visible,
            overwrite_policy=overwrite_policy,
        )
