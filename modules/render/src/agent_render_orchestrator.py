"""Agent: Render feature orchestrator.

Coordinates render capabilities through contracts only.

Agent layer:
- orchestration only
- zero I/O
- zero business logic
- zero domain computation
- depends only on contracts and taxonomy
"""

from __future__ import annotations

from modules.shared.src.render.contract_render_aggregate import IRenderAggregate
from modules.shared.src.render.contract_render_camera_config_protocol import IRenderCameraConfigProtocol
from modules.shared.src.render.contract_render_hdri_config_protocol import IRenderHdriConfigProtocol
from modules.shared.src.render.contract_render_scene_image_protocol import IRenderSceneImageProtocol
from modules.shared.src.render.contract_render_viewport_capture_protocol import IRenderViewportCaptureProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    CameraConfigVO,
    HdriConfigVO,
    RenderSceneVO,
    ViewportCaptureVO,
)


class RenderOrchestrator(IRenderAggregate):
    """Orchestrates render capabilities."""

    # ─── Block 1: definition + constructor ─────────────────────
    def __init__(
        self,
        viewport_capture: IRenderViewportCaptureProtocol,
        scene_image: IRenderSceneImageProtocol,
        camera_config: IRenderCameraConfigProtocol,
        hdri_config: IRenderHdriConfigProtocol,
    ) -> None:
        self._viewport_capture = viewport_capture
        self._scene_image = scene_image
        self._camera_config = camera_config
        self._hdri_config = hdri_config

    # ─── Block 2: aggregate methods only ──────────────────────
    async def capture_viewport(self, request: ViewportCaptureVO) -> ViewportCaptureVO:
        """FR-RND-001: delegate to viewport capture capability."""
        return await self._viewport_capture.capture_viewport(request)

    async def render_scene(self, request: RenderSceneVO) -> RenderSceneVO:
        """FR-RND-002: delegate to scene render capability."""
        return await self._scene_image.render_scene(request)

    async def configure_camera(self, request: CameraConfigVO) -> CameraConfigVO:
        """FR-RND-003: delegate to camera configuration capability."""
        return await self._camera_config.configure_camera(request)

    async def configure_hdri(self, request: HdriConfigVO) -> HdriConfigVO:
        """FR-RND-004: delegate to HDRI configuration capability."""
        return await self._hdri_config.configure_hdri(request)

    # ─── Block 3: dunders / factories / helpers ───────────────
    def __repr__(self) -> str:
        return "RenderOrchestrator()"
