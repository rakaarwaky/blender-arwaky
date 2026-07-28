"""Render domain contract: render aggregate.

FR-RND-001: viewport capture
FR-RND-002: scene rendering
FR-RND-003: camera configuration
FR-RND-004: HDRI lighting configuration

Agent implements this aggregate.
Surface layers depend on this facade.
"""

from __future__ import annotations

from .contract_render_protocol import (
    IRenderCameraConfigProtocol,
    IRenderHdriConfigProtocol,
    IRenderSceneImageProtocol,
    IRenderViewportCaptureProtocol,
)


class IRenderAggregate(
    IRenderViewportCaptureProtocol,
    IRenderSceneImageProtocol,
    IRenderCameraConfigProtocol,
    IRenderHdriConfigProtocol,
):
    """Facade for render feature behavior."""
