"""Scene feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/scene/)   → SceneInfo, request/response VOs
  - Contract (shared/src/scene/)   → SceneOperateProtocol, SceneInspectionPort
  - Capabilities                   → SceneOperateExecutor, SceneInspectionAdapter
  - Agent                          → SceneOrchestrator
  - Root                           → SceneContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_scene_container
from .root_scene_container import SceneContainer, create_scene_container

__all__ = [
    "SceneContainer",
    "create_scene_container",
    "root_scene_container",
]
