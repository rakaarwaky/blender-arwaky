"""Render domain contract: render aggregate.

FR-RND-001: viewport capture
FR-RND-002: scene rendering
FR-RND-003: camera configuration
FR-RND-004: HDRI lighting configuration

Agent implements this aggregate.
Surface layers depend on this facade.
"""

from __future__ import annotations

from .contract_render_camera_config_protocol import IRenderCameraConfigProtocol
from .contract_render_hdri_config_protocol import IRenderHdriConfigProtocol
from .contract_render_scene_image_protocol import IRenderSceneImageProtocol
from .contract_render_viewport_capture_protocol import IRenderViewportCaptureProtocol
from .taxonomy_render_vo import (
    CameraConfigVO,
    HdriConfigVO,
    RenderSceneVO,
    ViewportCaptureVO,
)


class IRenderAggregate(
    IRenderViewportCaptureProtocol,
    IRenderSceneImageProtocol,
    IRenderCameraConfigProtocol,
    IRenderHdriConfigProtocol,
):
    """Facade for render feature behavior."""


# Aggregate-level aliases: canonical request/result VOs exposed at the facade.
RenderSceneRequest = RenderSceneVO
ViewportCaptureRequest = ViewportCaptureVO
CameraConfigRequest = CameraConfigVO
HdriConfigRequest = HdriConfigVO
