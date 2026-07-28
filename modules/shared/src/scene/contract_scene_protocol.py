"""Scene domain contract: operation protocols.

FR-SCN-001: scene inspection protocol.
FR-SCN-002: scene cleanup protocol.

Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_command_vo import SceneCleanupVO, SceneInspectionVO


class ISceneInspectionProtocol(ABC):
    """Inbound contract for scene inspection capability."""

    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Inspect current scene state."""
        raise NotImplementedError


class ISceneCleanupProtocol(ABC):
    """Inbound contract for scene cleanup capability."""

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup or dry-run preview."""
        raise NotImplementedError
