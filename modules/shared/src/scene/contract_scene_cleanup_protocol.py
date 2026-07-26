"""Scene domain contract: scene cleanup protocol (ABC based).

Defines the protocol for safe cleanup operations on scene objects.
AES Contract layer — pure ABC definitions, no implementation.

FR-SCN-002: Cleanup Scene Objects
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_request_vo import SceneCleanupVO


class SceneCleanupProtocol(ABC):
    """Protocol for safe cleanup operations on scene objects.

    FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
    Supports dry-run preview mode.
    Unified VO (merged request + response) — no split classes.
    """

    @abstractmethod
    async def cleanup_scene_objects(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Execute cleanup of unwanted scene objects.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        pass
