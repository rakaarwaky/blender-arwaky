"""Common contract: Blender socket adapter port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_core_vo import (
    ImageBytes,
    MaxSize,
    ObjectName,
    PythonCode,
    StatusString,
)
from .taxonomy_vector3d_vo import Vector3D
from .taxonomy_scene_info_vo import SceneInfo
from .taxonomy_blender_object_entity import BlenderObject


# Type aliases for screenshot parameters
ViewAngle = str
ShadingMode = str


class ContractBlenderPort(ABC):
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
    async def get_object_info(
        self, name: ObjectName
    ) -> BlenderObject | None:
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
