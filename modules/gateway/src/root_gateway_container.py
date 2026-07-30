"""Composition root — DI wiring for the Gateway feature.

Wires capabilities to protocols and bootstraps the orchestrator.
Supports optional Launcher dependency for process-liveness integration.
"""

from modules.security.src.capabilities_code_validator import CodeValidator
from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionConfigVO
from modules.shared.src.launcher.contract_launcher_operate_aggregate import (
    ILauncherOperateAggregate,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ProbeDepth,
    RuntimeState,
)
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

    P1: Accepts optional ILauncherOperateAggregate to wire process-liveness
    into reconnect flow (FR-LAU-004 / Gateway reconnect consults Launcher).
    """

    def __init__(
        self,
        launcher: ILauncherOperateAggregate | None = None,
        connection_config: ConnectionConfigVO | None = None,
    ) -> None:
        self._launcher = launcher
        self._connection_config = connection_config or ConnectionConfigVO(
            host="localhost",
            port=9876,
            protocol_version="2.0.0",
        )

        self._transport = TransportExecutor(max_payload_bytes=10_485_760)

        self._connection = ConnectionExecutor(
            transport=self._transport,
            config=self._connection_config,
        )

        self._maintenance = MaintenanceExecutor(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=16.0,
            reconnect_fn=self._reconnect_with_runtime,
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

    def _reconnect_with_runtime(self) -> None:
        """FR-GWY-002 / P1: Reconnect consults Launcher runtime status.

        If Launcher is available, checks Blender process state before
        attempting socket reconnection. If state is not_running or stale,
        attempts to relaunch via Launcher. Raises on failure.
        """
        if self._launcher is not None:
            try:
                status = self._launcher.check_status(depth=ProbeDepth.FULL)
                if status.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                    # Attempt to relaunch Blender
                    launch = self._launcher.launch()
                    if not launch.success or not launch.ready:
                        raise RuntimeError(
                            f"Blender runtime not ready during Gateway reconnect: "
                            f"state={status.state.value}, launch_success={launch.success}"
                        )
            except Exception as exc:
                raise RuntimeError(f"Blender runtime check failed during reconnect: {exc}") from exc

        # Reconnect to socket
        self._connection.establish_connection()

    def get_orchestrator(self) -> GatewayOrchestrator:
        return self._orchestrator


def create_gateway_feature(
    launcher: ILauncherOperateAggregate | None = None,
    connection_config: ConnectionConfigVO | None = None,
) -> GatewayOrchestrator:
    """Factory function to create the gateway orchestrator.

    Args:
        launcher: Optional Launcher aggregate for process-liveness integration.
        connection_config: Optional connection configuration override.

    Returns:
        GatewayOrchestrator: Wired orchestrator ready for use.
    """
    container = GatewayContainer(launcher=launcher, connection_config=connection_config)
    return container.get_orchestrator()
