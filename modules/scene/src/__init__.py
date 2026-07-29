"""Scene feature module — AES implementation.

Layers:
  - Surface (modules/scene/src/surface_scene_command.py)
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

from .agent_scene_orchestrator import SceneOrchestrator

__all__ = [
    "SceneOrchestrator",
    "SceneContainer",
    "create_scene_container",
]


def __getattr__(name: str):
    """Lazy-load root module to break circular surface↔root import chain."""
    if name in ("SceneContainer", "create_scene_container"):
        from .root_scene_container import SceneContainer as _SceneContainer
        from .root_scene_container import create_scene_container as _create_scene_container
        if name == "SceneContainer":
            return _SceneContainer
        return _create_scene_container
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
