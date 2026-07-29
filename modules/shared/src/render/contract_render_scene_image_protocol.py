"""Render domain — FR-RND-002: Render scene image."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import RenderSceneVO


class IRenderSceneImageProtocol(ABC):
    @abstractmethod
    async def render_scene(self, request: RenderSceneVO) -> RenderSceneVO: ...
