"""Render feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/render/)
  - Contract (shared/src/render/)
  - Capabilities:
      - RenderViewportCaptureExecutor (FR-RND-001)
      - RenderSceneImageExecutor (FR-RND-002)
      - RenderCameraConfigExecutor (FR-RND-003)
      - RenderHdriConfigExecutor (FR-RND-004)
  - Agent:
      - RenderOrchestrator
  - Root:
      - RenderContainer
"""

from .agent_render_orchestrator import RenderOrchestrator
from .capabilities_render_camera_config_executor import RenderCameraConfigExecutor
from .capabilities_render_hdri_config_executor import RenderHdriConfigExecutor
from .capabilities_render_scene_image_executor import RenderSceneImageExecutor
from .capabilities_render_viewport_capture_executor import RenderViewportCaptureExecutor
from .root_render_container import RenderContainer, create_render_container

__all__ = [
    "RenderOrchestrator",
    "RenderCameraConfigExecutor",
    "RenderHdriConfigExecutor",
    "RenderSceneImageExecutor",
    "RenderViewportCaptureExecutor",
    "RenderContainer",
    "create_render_container",
]