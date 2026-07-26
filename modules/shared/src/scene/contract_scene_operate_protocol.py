"""Scene domain contract: scene operations protocol (ABC based).

FR-SCN-001, FR-SCN-002: Scene-level management with unified VOs.
Contract layer — pure ABC definitions, no implementation.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_scene_command_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)


class SceneOperateProtocol(ABC):
    """Protocol interface for scene-level management (cleanup, environment, metadata).

    FR-SCN-001: Enhanced inspection with detail level, hidden objects filter.
    FR-SCN-002: Cleanup with preservation policy, dry-run, child/dependent handling.
    Unified VO (merged request + response) — no split classes.
    """

    @abstractmethod
    async def cleanup_scene(
        self, request: SceneCleanupVO
    ) -> SceneCleanupVO:
        """Remove objects from scene based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        pass

    @abstractmethod
    async def get_scene_info(
        self, request: SceneInspectionVO
    ) -> SceneInspectionVO:
        """Retrieve current scene metadata and object tree.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        pass
