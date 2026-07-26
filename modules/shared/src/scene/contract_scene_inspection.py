"""Scene domain contract: scene inspection port interface.

FR-SCN-001: Scene inspection with detail level, hidden objects filter, summary mode.
FR-SCN-002: Cleanup delegation to object feature.
Contract layer — pure ABC definitions, no implementation.
Unified VO (merged request + response) — no split classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ObjectName, Prompt
from .taxonomy_scene_request_vo import SceneCleanupVO, SceneInspectionVO


class SceneInspectionPort(ABC):
    """Port interface for inspecting the Blender scene.

    FR-SCN-001: Supports detail levels (minimal, standard, detailed, summary),
    hidden objects filter, object type filter.
    Returns unified VO with scene state summary.
    """

    @abstractmethod
    async def get_scene_info(self, request: SceneInspectionVO) -> SceneInspectionVO:
        """Get detailed information about the current Blender scene.

        FR-SCN-001: Supports detail level, hidden objects filter, object type filter.
        Returns unified VO with scene state summary (SceneStateSummaryVO).
        """
        pass

    @abstractmethod
    async def get_object_info(
        self, object_name: ObjectName
    ) -> Prompt:
        """Get detailed information about a specific object by name."""
        pass

    @abstractmethod
    async def cleanup_scene(self, request: SceneCleanupVO) -> SceneCleanupVO:
        """Remove objects from scene based on preservation policy.

        FR-SCN-002: Supports preservation modes (keep cameras, lights, both, remove all).
        Supports dry-run preview mode.
        Returns unified VO with removed/preserved/skipped counts and references.
        Same structure for actual cleanup and dry-run preview.
        """
        pass
