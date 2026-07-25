"""Scene domain contract: scene inspection port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ObjectName, Prompt


class SceneInspectionPort(ABC):
    """Port interface for inspecting and cleaning the Blender scene."""

    @abstractmethod
    async def get_scene_info(self) -> Prompt:
        """Get detailed information about the current Blender scene."""
        pass

    @abstractmethod
    async def get_object_info(
        self, object_name: ObjectName
    ) -> Prompt:
        """Get detailed information about a specific object by name."""
        pass

    @abstractmethod
    async def cleanup_scene(self) -> Prompt:
        """Remove all objects from the scene."""
        pass
