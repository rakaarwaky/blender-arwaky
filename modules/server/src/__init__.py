"""Server feature module — Blender TCP/stdio socket communication.

Layers:
  - agent_server_orchestrator.py → Agent: ServerOrchestrator (IBlenderServerAggregate)
  - capabilities_blender_connection.py → Capabilities: BlenderConnection, BlenderConnectionFactory
  - capabilities_blender_socket_adapter.py → Capabilities: BlenderSocketAdapter
  - capabilities_code_execution_adapter.py → Capabilities: CodeExecutionAdapter
  - capabilities_blender_command_adapter.py → Capabilities: BlenderCommandAdapter
  - surface_socket_command.py → Surface: BlenderSocketCommandSurface
  - root_server_container.py → Root: ServerContainer
  - root_server_entry.py → Root: create_server_entry, start_server
"""

from .agent_server_orchestrator import ServerOrchestrator
from .capabilities_blender_command_adapter import BlenderCommandAdapter
from .capabilities_blender_connection import BlenderConnection, BlenderConnectionFactory
from .capabilities_blender_socket_adapter import BlenderSocketAdapter
from .capabilities_code_execution_adapter import CodeExecutionAdapter
from .surface_socket_command import BlenderSocketCommandSurface
from .root_server_container import ServerContainer
from .root_server_entry import create_server_entry, start_server

__all__ = [
    # Agent
    "ServerOrchestrator",
    # Capabilities
    "BlenderCommandAdapter",
    "BlenderConnection",
    "BlenderConnectionFactory",
    "BlenderSocketAdapter",
    "CodeExecutionAdapter",
    # Surface
    "BlenderSocketCommandSurface",
    # Root
    "ServerContainer",
    "create_server_entry",
    "start_server",
]
