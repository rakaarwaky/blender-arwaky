"""Launcher feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/launcher/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/launcher/)   → 5 individual protocols + Aggregate ABC
  - Capabilities (5 executors)        → One per FR-LAU operation
  - Agent                             → LauncherOrchestrator (implements Aggregate facade)
  - Root                              → LauncherContainer (DI wiring)
"""

from .agent_orchestrator import LauncherOrchestrator
from .capabilities_locate_register_executor import LocateRegisterExecutor
from .capabilities_launch_executor import LaunchExecutor
from .capabilities_shutdown_executor import ShutdownExecutor
from .capabilities_runtime_status_executor import RuntimeStatusExecutor
from .capabilities_persist_state_executor import PersistStateExecutor
from . import root_launcher_container
from .root_launcher_container import LauncherContainer, create_launcher_feature

__all__ = [
    "LauncherContainer",
    "create_launcher_feature",
    "LauncherOrchestrator",
    "LocateRegisterExecutor",
    "LaunchExecutor",
    "ShutdownExecutor",
    "RuntimeStatusExecutor",
    "PersistStateExecutor",
    "root_launcher_container",
]
