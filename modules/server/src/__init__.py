"""Server feature module — Blender TCP socket communication.

Layers:
  - Taxonomy (shared): ConnectionStatus, ExecutionResult, TaskStatus, ConnectionConfig, errors, constants
  - Contracts (shared): IBlenderServerAggregate, protocol ABCs
  - Utility (shared): IO, message framing, string helpers, time utils, AST validator
  - Capabilities: BlenderConnection, BlenderSocketAdapter, CodeExecutionAdapter,
                  BlenderCommandAdapter, ExecutionQueue, TaskManager
  - Agent: ServerOrchestrator (IBlenderServerAggregate)
  - Root: ServerContainer (DI container wiring all layers)

Note: No Surface layer — server is an internal module.
Surface handlers live in CLI and MCP modules.
"""

from .agent_server_orchestrator import ServerOrchestrator
from .capabilities_blender_command_adapter import BlenderCommandAdapter
from .capabilities_blender_connection import BlenderConnection, BlenderConnectionFactory
from .capabilities_blender_socket_adapter import BlenderSocketAdapter
from .capabilities_code_execution_adapter import CodeExecutionAdapter
from .capabilities_server_queue import ExecutionQueue
from .capabilities_server_task_manager import TaskManager
from .root_server_container import ServerContainer, create_container

__all__ = [
    # ─── Agent ────────────────────────────────────────────────
    "ServerOrchestrator",
    # ─── Capabilities ─────────────────────────────────────────
    "BlenderCommandAdapter",
    "BlenderConnection",
    "BlenderConnectionFactory",
    "BlenderSocketAdapter",
    "CodeExecutionAdapter",
    "ExecutionQueue",
    "TaskManager",
    # ─── Root (DI Container) ──────────────────────────────────
    "ServerContainer",
    "create_container",
]
