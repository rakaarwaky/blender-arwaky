"""Scene domain contract: scene cleanup protocol (ABC based).

Defines the protocol for safe cleanup operations on scene objects.
AES Contract layer — pure ABC definitions, no implementation.

FR-SCN-002: Cleanup Scene Objects
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import CleanupMode, ErrorString, ObjectName
from .taxonomy_scene_request_vo import CleanupSceneRequestVO


class SceneCleanupProtocol(ABC):
    """Protocol for safe cleanup operations on scene objects."""

    @abstractmethod
    async def cleanup_scene_objects(self, request: CleanupSceneRequestVO) -> dict:
        """Execute cleanup of unwanted scene objects.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns detailed report of removed, preserved, and skipped objects.
        """
        pass
