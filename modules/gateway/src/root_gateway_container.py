"""Composition root — DI wiring for the Gateway feature.

Wires capabilities to protocols and bootstraps the orchestrator.
"""

from .agent_gateway_orchestrator import GatewayOrchestrator
from .capabilities_code_execution_executor import CodeExecutionExecutor
from .capabilities_connection_executor import ConnectionExecutor
from .capabilities_maintenance_executor import MaintenanceExecutor
from .capabilities_scene_queue_executor import SceneQueueExecutor
from .capabilities_transport_executor import TransportExecutor


class GatewayContainer:
    """Dependency injection container for the Gateway feature.

    Wires all 5 capabilities and composes the orchestrator.
    """

    def __init__(self) -> None:
        self._connection = ConnectionExecutor()
        self._maintenance = MaintenanceExecutor()
        self._transport = TransportExecutor(max_payload_bytes=10_485_760)
        self._scene_queue = SceneQueueExecutor(max_depth=50, wait_timeout_seconds=30.0)
        self._code_executor = CodeExecutionExecutor(max_output_bytes=1_048_576)
        self._orchestrator = GatewayOrchestrator(
            self._connection,
            self._maintenance,
            self._transport,
            self._scene_queue,
            self._code_executor,
        )

    def get_orchestrator(self) -> GatewayOrchestrator:
        return self._orchestrator


def create_gateway_feature() -> GatewayOrchestrator:
    """Factory function to create the gateway orchestrator.

    Returns:
        GatewayOrchestrator: Wired orchestrator ready for use.
    """
    container = GatewayContainer()
    return container.get_orchestrator()
