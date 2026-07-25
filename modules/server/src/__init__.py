"""Server feature module — Blender TCP socket communication.

Layers:
  - agent_server_orchestrator.py → Agent: ServerOrchestrator (IBlenderServerAggregate)
  - capabilities_blender_connection.py → Capabilities: BlenderConnection, BlenderConnectionFactory
  - capabilities_blender_socket_adapter.py → Capabilities: BlenderSocketAdapter
  - capabilities_code_execution_adapter.py → Capabilities: CodeExecutionAdapter
  - capabilities_blender_command_adapter.py → Capabilities: BlenderCommandAdapter
  - capabilities_server_queue.py → Capabilities: ExecutionQueue (IExecutionQueueProtocol)
  - capabilities_server_task_manager.py → Capabilities: TaskManager (ITaskManagerProtocol)
"""

from .agent_server_orchestrator import ServerOrchestrator
from .capabilities_blender_command_adapter import BlenderCommandAdapter
from .capabilities_blender_connection import BlenderConnection, BlenderConnectionFactory
from .capabilities_blender_socket_adapter import BlenderSocketAdapter
from .capabilities_code_execution_adapter import CodeExecutionAdapter
from .capabilities_server_queue import ExecutionQueue
from .capabilities_server_task_manager import TaskManager

__all__ = [
    # Agent
    "ServerOrchestrator",
    # Capabilities
    "BlenderCommandAdapter",
    "BlenderConnection",
    "BlenderConnectionFactory",
    "BlenderSocketAdapter",
    "CodeExecutionAdapter",
    "ExecutionQueue",
    "TaskManager",
]
