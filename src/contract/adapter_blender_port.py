"""
Contract: Port interface for Blender socket adapter.

This port defines the interface that all Blender connection adapters must implement.
AES Port layer — depends only on taxonomy entities.
"""

from abc import ABC, abstractmethod

from taxonomy import BlenderObject, ImageBytes, MaxSize, ObjectName, PythonCode, SceneInfo, StatusString

# Type aliases for screenshot parameters
ViewAngle = str
ShadingMode = str


class BlenderPort(ABC):
    """Port interface for low-level Blender operations via socket connection."""

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
        view_angle: ViewAngle = "PERSPECTIVE",
        shading_mode: ShadingMode = "MATERIAL",
        show_overlays: bool = True,
        focus_object: ObjectName | None = None,
    ) -> tuple[ImageBytes, int, int]:
        """Capture viewport screenshot. Returns (image_bytes, width, height)."""
        pass
