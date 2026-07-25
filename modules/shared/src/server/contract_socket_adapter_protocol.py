"""Contract: Protocol for Blender socket adapter operations.

Implemented by Capabilities that handle low-level Blender operations
via socket connection (execute_code, get_scene_info, get_object_info,
get_screenshot).
AES Protocol layer — depends only on Taxonomy.
"""

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ImageBytes, MaxSize, ObjectName, PythonCode, StatusString
from ..object.taxonomy_blender_object_entity import BlenderObject
from ..scene.taxonomy_scene_info_vo import SceneInfo


class IBlenderSocketAdapterProtocol(ABC):
    """Protocol for low-level Blender operations via socket connection."""

    @abstractmethod
    async def execute_code(self, code: PythonCode) -> StatusString:
        """Execute arbitrary Python code in Blender and return result."""
        pass

    @abstractmethod
    async def get_scene_info(self) -> SceneInfo:
        """Retrieve current scene information."""
        pass

    @abstractmethod
    async def get_object_info(self, name: ObjectName) -> BlenderObject | None:
        """Get information about a specific object by name."""
        pass

    @abstractmethod
    async def get_screenshot(
        self,
        max_size: MaxSize | None = None,
        view_angle: str = "PERSPECTIVE",
        shading_mode: str = "MATERIAL",
        show_overlays: bool = True,
        focus_object: ObjectName | None = None,
    ) -> tuple[ImageBytes, int, int]:
        """Capture viewport screenshot. Returns (image_bytes, width, height)."""
        pass
