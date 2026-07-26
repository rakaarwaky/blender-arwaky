"""Scene domain contract: scene inspection protocol (ABC based).

AES Contract layer — pure ABC definition, no implementation.

FR-SCN-001: Inspect Scene State
- Returns a structured overview of the active scene (object count, cameras,
  lights, render settings summary, scene metadata)
- Inspection is strictly read-only; must not mutate scene state
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import SuccessFlag
from .taxonomy_scene_vo import GetSceneInfoVO


class SceneInspectProtocol(ABC):
    """Protocol for read-only inspection of the active scene."""

    @abstractmethod
    def inspect_scene(
        self,
        detail_level: str = "standard",
        include_hidden: bool = False,
    ) -> GetSceneInfoVO:
        """Return a structured scene overview.

        FR-SCN-001: Read-only. Never mutates scene state. `detail_level`
        controls verbosity; `include_hidden` toggles hidden-object inclusion.
        """
        pass
