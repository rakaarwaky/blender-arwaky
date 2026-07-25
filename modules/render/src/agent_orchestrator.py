"""Agent: Render feature orchestrator.

Coordinates viewport capture, image rendering, camera, and HDRI setup.
"""

import logging
from typing import Any

from modules.shared.src.render.contract_render_operate_protocol import RenderOperateProtocol
from modules.shared.src.render.taxonomy_render_request_vo import (
    GetScreenshotRequestVO,
    RenderRequestVO,
    RenderResponseVO,
    ScreenshotResponseVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RenderOrchestrator:
    """Orchestrates render operations."""

    def __init__(self, executor: RenderOperateProtocol):
        self._executor = executor

    async def get_screenshot(self, request: GetScreenshotRequestVO) -> ScreenshotResponseVO:
        return await self._executor.get_screenshot(request)

    async def render(self, request: RenderRequestVO) -> RenderResponseVO:
        return await self._executor.render(request)
