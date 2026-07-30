"""Composition root — DI wiring for the Gateway feature.

Wires capabilities to protocols and bootstraps the orchestrator.
"""

from modules.security.src.capabilities_code_validator import CodeValidator
from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionConfigVO
from modules.shared.src.security.taxonomy_security_vo import SecurityPolicyVO

from .agent_gateway_orchestrator import GatewayOrchestrator
from .capabilities_code_execution import CodeExecutionExecutor
from .capabilities_connection_maintenance import MaintenanceExecutor
from .capabilities_connection_manager import ConnectionExecutor
from .capabilities_scene_queue import SceneQueueExecutor
from .capabilities_transport_executor import TransportExecutor


class GatewayContainer:
    """Dependency injection container for the Gateway feature.

    Wires all 5 capabilities and composes the orchestrator.
    ConnectionExecutor receives TransportProtocol + config.
    CodeExecutionExecutor receives security policy + transport.
    MaintenanceExecutor receives retry configuration.
    """

    def __init__(self) -> None:
        self._transport = TransportExecutor(max_payload_bytes=10_485_760)

        self._connection = ConnectionExecutor(
            transport=self._transport,
            config=ConnectionConfigVO(host="localhost", port=9876),
        )

        self._maintenance = MaintenanceExecutor(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=16.0,
            reconnect_fn=self._connection.establish_connection,
        )

        self._scene_queue = SceneQueueExecutor(max_depth=50, wait_timeout_seconds=30.0)

        self._code_executor = CodeExecutionExecutor(
            security_policy=CodeValidator(policy=SecurityPolicyVO()),
            transport=self._transport,
            max_output_bytes=1_048_576,
            execution_timeout_seconds=30.0,
        )

        self._orchestrator = GatewayOrchestrator(
            connection=self._connection,
            maintenance=self._maintenance,
            transport=self._transport,
            scene_queue=self._scene_queue,
            code_executor=self._code_executor,
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
