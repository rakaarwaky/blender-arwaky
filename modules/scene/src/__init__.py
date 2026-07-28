"""Scene feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/scene/)
  - Contract (shared/src/scene/)
  - Capabilities:
      - SceneInspectionExecutor (FR-SCN-001)
      - SceneCleanupExecutor (FR-SCN-002)
  - Agent:
      - SceneOrchestrator
  - Root:
      - SceneContainer
"""

from .root_scene_container import SceneContainer, create_scene_container

__all__ = [
    "SceneContainer",
    "create_scene_container",
]