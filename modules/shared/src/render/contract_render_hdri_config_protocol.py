"""Render domain — FR-RND-004: Configure HDRI lighting."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_render_vo import HdriConfigVO


class IRenderHdriConfigProtocol(ABC):
    @abstractmethod
    async def configure_hdri(self, request: HdriConfigVO) -> HdriConfigVO: ...
