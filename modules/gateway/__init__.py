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
from .src.capabilities_code_execution_executor import CodeExecutionExecutor
from .src.capabilities_connection_executor import ConnectionExecutor
from .src.capabilities_maintenance_executor import MaintenanceExecutor
from .src.capabilities_scene_queue_executor import SceneQueueExecutor
from .src.capabilities_transport_executor import TransportExecutor

__all__ = [
    "GatewayOrchestrator",
    "ConnectionExecutor",
    "MaintenanceExecutor",
    "TransportExecutor",
    "SceneQueueExecutor",
    "CodeExecutionExecutor",
]
