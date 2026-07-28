"""Scene domain contract: operation protocols.

FR-SCN-001: Scene inspection protocol.
FR-SCN-002: Scene cleanup protocol.

Contract layer — pure behavior definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_command_vo import SceneCleanupVO, SceneInspectionVO


class SceneInspectionProtocol(ABC):
    """Inbound contract for scene inspection capability."""

    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Inspect current scene state and return a structured summary."""
        raise NotImplementedError


class SceneCleanupProtocol(ABC):
    """Inbound contract for scene cleanup capability."""

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup or dry-run preview and return a cleanup report."""
        raise NotImplementedError