"""Scene snapshot and render engine constants."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final
from uuid import UUID

from .constant_core_types import BlenderObjectList, ErrorString, ObjectId, ObjectName, RenderEngine
from .vo_bounding_box import BoundingBox
from .vo_vector3d import Vector3D

# ============================================================
# RENDER ENGINE CONSTANTS
# ============================================================

RENDER_ENGINE_CYCLES: Final[RenderEngine] = RenderEngine("CYCLES")
RENDER_ENGINE_EEVEE: Final[RenderEngine] = RenderEngine("EEVEE")


# ============================================================
# READ MODEL: SceneInfo
# ============================================================


@dataclass
class SceneInfo:
    """Snapshot of the entire scene for external consumption."""

    objects: BlenderObjectList
    active_object_id: ObjectId | None = None
    render_engine: RenderEngine = RENDER_ENGINE_CYCLES
    resolution: Vector3D = field(default_factory=lambda: Vector3D(1920, 1080, 1))
