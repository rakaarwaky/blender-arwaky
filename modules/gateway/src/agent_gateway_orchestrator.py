"""Gateway orchestrator — Aggregate facade coordinating connection, transport, and execution.

FR-GWY: Coordinates connection, maintenance, transport, and code execution
via individual protocol delegation. Scene queue coordination is delegated
to GatewaySceneCoordinator to keep type count under AES405 limit.
"""

import logging

from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
)
from modules.shared.src.gateway.contract_connection_protocol import (
    ConnectionProtocol,
)
from modules.shared.src.gateway.contract_maintenance_protocol import (
    ConnectionMaintenanceProtocol,
)
from modules.shared.src.gateway.contract_scene_queue_protocol import (
    SceneQueueProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionOutcomeVO,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
)

from .utility_scene_coordinator import SceneCoordinatorUtility

from modules.shared.src.gateway.contract_gateway_aggregate import IBlenderServerAggregate

logger = logging.getLogger("BlenderMCPServer")


class GatewayOrchestrator(IBlenderServerAggregate):
    """Aggregate facade for the Gateway feature.

    Coordinates connection, transport, and execution via protocol delegation.
    Scene queue coordination is delegated to GatewaySceneCoordinator.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        connection: ConnectionProtocol,
        maintenance: ConnectionMaintenanceProtocol,
        transport: TransportProtocol,
        scene_queue: SceneQueueProtocol,
        code_executor: CodeExecutionProtocol,
    ) -> None:
        self._connection = connection
        self._maintenance = maintenance
        self._transport = transport
        self._coordinator = SceneCoordinatorUtility(scene_queue)
        self._code_executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    def establish_connection(self) -> ConnectionOutcomeVO:
        """FR-GWY-001: Establish connection and wire transport layer."""
        logger.info("Establishing gateway connection")
        result = self._connection.establish_connection()

        # Wire connection to transport and maintenance
        if result.state.value == "connected":
            self._maintenance.set_state(result.state)

        return result

    def disconnect(self) -> None:
        """FR-GWY-002: Graceful disconnect."""
        logger.info("Disconnecting gateway")
        self._connection.disconnect()
        self._maintenance.set_state(None)

    def get_connection_status(self) -> ConnectionStatusVO:
        """FR-GWY-002: Query connection state."""
        return self._maintenance.get_connection_status()

    def send_heartbeat(self) -> None:
        """FR-GWY-002: Send heartbeat."""
        self._maintenance.send_heartbeat()

    def attempt_reconnect(self) -> ConnectionStatusVO:
        """FR-GWY-002: Attempt reconnection."""
        return self._maintenance.attempt_reconnect()

    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
        """FR-GWY-003: Send transport request and receive response."""
        logger.debug("Sending transport request: %s", request.tracking_id)
        return self._transport.send_request(request)

    def enqueue_scene_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        """FR-GWY-004: Enqueue scene operation — delegated to coordinator."""
        return self._coordinator.enqueue_scene_operation(operation)

    def get_queue_status(self) -> QueueStatusVO:
        """FR-GWY-004: Get queue status — delegated to coordinator."""
        return self._coordinator.get_queue_status()

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        """FR-GWY-005: Execute raw Python code."""
        logger.debug("Executing code: tracking_id=%s", request.tracking_id)
        return self._code_executor.execute_code(request)
