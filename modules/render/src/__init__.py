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

from .root_render_container import RenderContainer, create_render_container

__all__ = [
    "RenderContainer",
    "create_render_container",
]