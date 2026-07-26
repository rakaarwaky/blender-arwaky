"""Server feature module — Blender TCP socket communication.

Layers:
  - Taxonomy (shared): ConnectionStatus, ExecutionResult, TaskStatus, ConnectionConfig, errors, constants
  - Contracts (shared): IBlenderServerAggregate, protocol ABCs
  - Utility (shared): IO, message framing, string helpers, time utils, AST validator
  - Capabilities (3 FR modules):
      1. capabilities_blender_connection (FR-001 Connection)
      2. capabilities_code_execution_adapter (FR-002 Code Execution & TaskManager)
      3. capabilities_blender_command_adapter (FR-003 Command Dispatch & ExecutionQueue)
  - Agent: ServerOrchestrator (IBlenderServerAggregate)
  - Root: ServerContainer (DI container wiring all layers)

Note: No Surface layer — server is an internal module.
Surface handlers live in CLI and MCP modules.
"""

from .agent_server_orchestrator import ServerOrchestrator
from .capabilities_blender_command_adapter import BlenderCommandAdapter
from .capabilities_blender_connection import BlenderConnection
from .capabilities_code_execution_adapter import CodeExecutionAdapter
from .root_server_container import ServerContainer, create_container

__all__ = [
    # ─── Agent ────────────────────────────────────────────────
    "ServerOrchestrator",
    # ─── Capabilities (Aligned with 3 FRs) ────────────────────
    "BlenderCommandAdapter",
    "BlenderConnection",
    "CodeExecutionAdapter",
    # ─── Root (DI Container) —─────────────────────────────────
    "ServerContainer",
    "create_container",
]
