"""Gateway orchestrator — Aggregate facade coordinating gateway protocols.

FR-GWY: Coordinates connection, maintenance, transport, scene queue, and code execution.
"""

from __future__ import annotations

import logging

from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
)
from modules.shared.src.gateway.contract_connection_protocol import (
    ConnectionProtocol,
)
from modules.shared.src.gateway.contract_gateway_aggregate import IGatewayAggregate
from modules.shared.src.gateway.contract_scene_queue_protocol import (
    SceneQueueProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    ConnectionClosedError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionOutcomeVO,
    ConnectionState,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
)
from modules.shared.src.launcher.contract_launcher_operate_aggregate import (
    ILauncherOperateAggregate,
)

from .capabilities_connection_maintenance import MaintenanceExecutor

logger = logging.getLogger("BlenderMCPServer")


class GatewayOrchestrator(IGatewayAggregate):
    """Aggregate facade for the Gateway feature."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        connection: ConnectionProtocol,
        transport: TransportProtocol,
        scene_queue: SceneQueueProtocol,
        code_executor: CodeExecutionProtocol,
        launcher: ILauncherOperateAggregate | None = None,
        max_retries: int = 3,
        base_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 16.0,
    ) -> None:
        self._connection = connection
        self._transport = transport
        self._scene_queue = scene_queue
        self._code_executor = code_executor
        self._launcher = launcher
        self._maintenance = MaintenanceExecutor(
            max_retries=max_retries,
            base_backoff_seconds=base_backoff_seconds,
            max_backoff_seconds=max_backoff_seconds,
            reconnect_fn=self._reconnect_with_runtime,
        )

    # ─── Block 2: Protocol Method Implementation ─────────────

    def establish_connection(self) -> ConnectionOutcomeVO:
        """FR-GWY-001: Establish connection and wire transport layer."""
        logger.info("Establishing gateway connection")
        result = self._connection.establish_connection()

        if result.state == ConnectionState.CONNECTED:
            self._maintenance.set_state(result.state)

        return result

    def disconnect(self) -> None:
        """FR-GWY-002: Graceful disconnect.

        Fails pending queued ops before closing connection to ensure
        deterministic failure rather than silent drop.
        """
        logger.info("Disconnecting gateway")
        if hasattr(self._scene_queue, 'fail_pending'):
            self._scene_queue.fail_pending(
                ConnectionClosedError(details={"reason": "graceful_disconnect"})
            )
        self._connection.disconnect()
        self._maintenance.set_state(ConnectionState.CLOSED)

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
        """FR-GWY-004: Enqueue scene operation."""
        return self._scene_queue.enqueue_operation(operation)

    def get_queue_status(self) -> QueueStatusVO:
        """FR-GWY-004: Get queue status."""
        return self._scene_queue.get_queue_status()

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        """FR-GWY-005: Execute raw Python code."""
        logger.debug("Executing code: tracking_id=%s", request.tracking_id)
        return self._code_executor.execute_code(request)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _reconnect_with_runtime(self) -> None:
        """FR-GWY-002 / FR-LAU-004: Reconnect consults Launcher runtime status.

        Orchestration logic: probe launcher → launch if stale → reconnect.
        Moved from root container to agent layer (AES201 compliance).
        """
        if self._launcher is not None:
            from modules.shared.src.launcher.taxonomy_launcher_vo import (
                ProbeDepth,
                RuntimeState,
            )

            try:
                status = self._launcher.check_status(depth=ProbeDepth.FULL)
                if status.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                    launch = self._launcher.launch()
                    if not launch.success or not launch.ready:
                        raise RuntimeError(
                            f"Blender runtime not ready during Gateway reconnect: "
                            f"state={status.state.value}, launch_success={launch.success}"
                        )
            except Exception as exc:
                raise RuntimeError(
                    f"Blender runtime check failed during reconnect: {exc}"
                ) from exc

        self._connection.establish_connection()

    def __repr__(self) -> str:
        return (
            f"GatewayOrchestrator("
            f"connection={self._connection is not None}, "
            f"transport={self._transport is not None}, "
            f"scene_queue={self._scene_queue is not None}, "
            f"code_executor={self._code_executor is not None}, "
            f"launcher={self._launcher is not None}"
            f")"
        )
