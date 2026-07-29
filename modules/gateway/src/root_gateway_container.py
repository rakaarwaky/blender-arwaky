"""Composition root — DI wiring for the Gateway feature.

Wires capabilities to protocols and bootstraps the orchestrator.
"""

from modules.security.src.capabilities_code_validator import CodeValidator
from modules.shared.src.security.taxonomy_security_vo import SecurityPolicyVO

from .agent_gateway_orchestrator import GatewayOrchestrator
from .capabilities_code_execution import CodeExecutionExecutor
from .capabilities_connection_maintenance import MaintenanceExecutor
from .capabilities_connection_manager import ConnectionExecutor
from .capabilities_scene_queue import SceneQueueExecutor
from .capabilities_transport_executor import TransportExecutor
from .utility_scene_coordinator import SceneCoordinatorUtility


class GatewayContainer:
    """Dependency injection container for the Gateway feature.

    Wires all 5 capabilities and composes the orchestrator.
    ConnectionExecutor receives TransportProtocol + config.
    CodeExecutionExecutor receives security policy + transport.
    MaintenanceExecutor receives retry configuration.
    """

    def __init__(self) -> None:
        # Create security policy (dependency of CodeExecutionExecutor)
        self._security_policy = CodeValidator(policy=SecurityPolicyVO())

        # Create transport (dependency of ConnectionExecutor + CodeExecutionExecutor)
        self._transport = TransportExecutor(max_payload_bytes=10_485_760)

        # Wire ConnectionExecutor with transport + config
        from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionConfigVO

        self._connection = ConnectionExecutor(
            transport=self._transport,
            config=ConnectionConfigVO(host="localhost", port=50051),
        )

        # Wire MaintenanceExecutor with retry config + real reconnect hook.
        # reconnect_fn drives FR-GWY-002 retry: each attempt calls the
        # ConnectionExecutor; exhaustion transitions the connection to FAILED.
        self._maintenance = MaintenanceExecutor(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=16.0,
            reconnect_fn=self._connection.establish_connection,
        )

        # Wire SceneQueueExecutor + Coordinator (delegated to keep orchestrator under AES405 limit)
        self._scene_queue = SceneQueueExecutor(max_depth=50, wait_timeout_seconds=30.0)
        self._scene_coordinator = SceneCoordinatorUtility(self._scene_queue)

        # Wire CodeExecutionExecutor with security policy + transport
        self._code_executor = CodeExecutionExecutor(
            security_policy=self._security_policy,
            transport=self._transport,
            max_output_bytes=1_048_576,
            execution_timeout_seconds=30.0,
        )

        # Compose orchestrator (scene coordination via coordinator class)
        self._orchestrator = GatewayOrchestrator(
            self._connection,
            self._maintenance,
            self._transport,
            self._scene_coordinator,
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
