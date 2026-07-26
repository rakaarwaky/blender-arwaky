"""Agent: Render feature orchestrator.

Coordinates viewport capture, image rendering, camera setup, and render
configuration through the RenderOperateProtocol capability layer.
"""

from __future__ import annotations

import logging

from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.render.taxonomy_render_vo import (
    GetScreenshotVO,
    RenderVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderOrchestrator:
    """Orchestrates render operations via capability protocol."""

    def __init__(self, executor: RenderOperateProtocol) -> None:
        self._executor = executor

    async def get_screenshot(self, request: GetScreenshotVO) -> GetScreenshotVO:
        return await self._executor.get_viewport_screenshot(request)

    async def render(self, request: RenderVO) -> RenderVO:
        return await self._executor.render(request)
