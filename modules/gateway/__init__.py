"""Gateway module — Blender connection, transport, queue, and raw code execution.

Layers:
  - Taxonomy (shared/src/gateway/)   → VOs, Errors
  - Contract (shared/src/gateway/)   → 5 protocols (connection, maintenance,
                                        transport, scene queue, code execution)
  - Capabilities (5 executors)       → One per FR-GWY operation
  - Agent                            → GatewayOrchestrator (Aggregate facade)
  - Root                             → GatewayContainer (DI wiring)
"""

from .src.agent_gateway_orchestrator import GatewayOrchestrator
from .src.capabilities_code_execution import CodeExecutionAdapter, CodeExecutionExecutor, TaskEntry
from .src.capabilities_connection_manager import BlenderConnection, ConnectionExecutor
from .src.capabilities_connection_maintenance import MaintenanceExecutor
from .src.capabilities_scene_queue import OperationQueue, OperationState, SceneQueueExecutor
from .src.capabilities_transport_executor import BlenderCommandAdapter, TransportExecutor

__all__ = [
    "GatewayOrchestrator",
    "BlenderConnection",
    "ConnectionExecutor",
    "MaintenanceExecutor",
    "BlenderCommandAdapter",
    "TransportExecutor",
    "OperationQueue",
    "OperationState",
    "SceneQueueExecutor",
    "CodeExecutionAdapter",
    "CodeExecutionExecutor",
    "TaskEntry",
]
