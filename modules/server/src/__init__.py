"""Server feature module — Blender TCP/stdio socket communication.

Layers:
  - agent_server_orchestrator.py → Agent: ServerOrchestrator (IBlenderServerAggregate)
  - capabilities_blender_connection.py → Capabilities: BlenderConnection, BlenderConnectionFactory
  - capabilities_blender_socket_adapter.py → Capabilities: BlenderSocketAdapter
  - capabilities_code_execution_adapter.py → Capabilities: CodeExecutionAdapter
"""

from .agent_server_orchestrator import ServerOrchestrator
from .capabilities_blender_connection import BlenderConnection, BlenderConnectionFactory
from .capabilities_blender_socket_adapter import BlenderSocketAdapter
from .capabilities_code_execution_adapter import CodeExecutionAdapter

__all__ = [
    "ServerOrchestrator",
    "BlenderConnection",
    "BlenderConnectionFactory",
    "BlenderSocketAdapter",
    "CodeExecutionAdapter",
]
