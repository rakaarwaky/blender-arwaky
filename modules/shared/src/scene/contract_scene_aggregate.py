"""Aggregate contract for the scene feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_scene_cleanup_protocol import SceneCleanupProtocol
from .contract_scene_inspection import SceneInspectionPort
from .contract_scene_operate_protocol import SceneOperateProtocol

__all__ = [
    "SceneCleanupProtocol",
    "SceneInspectionPort",
    "SceneOperateProtocol",
]
