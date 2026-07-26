"""Render feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/render/)   → Request/response VOs
  - Contract (shared/src/render/)   → RenderOperateProtocol, ViewportCapturePort
  - Capabilities                   → RenderOperateExecutor
  - Agent                          → RenderOrchestrator
  - Root                           → RenderContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_render_container
from .root_render_container import RenderContainer, create_render_container

__all__ = [
    "RenderContainer",
    "create_render_container",
    "root_render_container",
]