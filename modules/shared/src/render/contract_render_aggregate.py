"""Render domain contract: render aggregate.

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