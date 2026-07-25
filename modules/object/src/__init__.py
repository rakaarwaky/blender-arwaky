"""Object feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/object/)   → VOs, Entities, Events, Errors, Constants
  - Contract (shared/src/object/)   → Protocol + Aggregate ABCs
  - Capabilities                     → ObjectOperateExecutor (implements Protocol)
  - Agent                            → ObjectOrchestrator (implements Aggregate)
  - Root                             → ObjectContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_object_container
from .root_object_container import ObjectContainer, create_object_feature

__all__ = [
    "ObjectContainer",
    "create_object_feature",
    "root_object_container",
]
