"""Launcher feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/launcher/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/launcher/)   → 5 individual protocols + Aggregate ABC
  - Capabilities (5 executors)        → One per FR-LAU operation
  - Agent                             → LauncherOrchestrator (implements Aggregate facade)
  - Root                              → LauncherContainer (DI wiring)
"""

from . import root_launcher_container
from .root_launcher_container import LauncherContainer, create_launcher_feature

__all__ = [
    "LauncherContainer",
    "create_launcher_feature",
    "root_launcher_container",
]
