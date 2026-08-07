"""Composition root — DI wiring for the Gateway feature.

Wires capabilities to protocols and bootstraps the orchestrator.
All dependencies injected — zero cross-feature imports, zero business logic.
"""

from modules.shared.src.gateway.contract_code_validation_protocol import (
    CodeValidationProtocol,
)
from modules.shared.src.gateway.contract_gateway_aggregate import IGatewayAggregate
from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionConfigVO
from modules.shared.src.launcher.contract_launcher_operate_aggregate import (
    ILauncherOperateAggregate,
)

from .agent_gateway_orchestrator import GatewayOrchestrator
from .capabilities_code_execution import CodeExecutionExecutor
from .capabilities_connection_maintenance import MaintenanceExecutor
from .capabilities_connection_manager import ConnectionExecutor
from .capabilities_scene_queue import SceneQueueExecutor
from .capabilities_transport_executor import TransportExecutor
from .taxonomy_gateway_constant import (
    DEFAULT_EXECUTION_TIMEOUT_SECONDS,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_MAX_PAYLOAD_BYTES,
)


class GatewayContainer:
    """Dependency injection container for the Gateway feature.

    Wires all 5 capabilities and composes the orchestrator.
    All dependencies must be injected — no cross-feature imports allowed.
    """

    def __init__(
        self,
        launcher: ILauncherOperateAggregate | None = None,
        connection_config: ConnectionConfigVO | None = None,
        code_validation: CodeValidationProtocol | None = None,
    ) -> None:
        self._launcher = launcher
        self._connection_config = connection_config or ConnectionConfigVO(
            host="localhost",
            port=50051,
            protocol_version="2.0.0",
        )

        if code_validation is None:
            raise ValueError(
                "GatewayContainer requires a CodeValidationProtocol instance. "
                "The caller (entry point) must provide one."
            )

        self._transport = TransportExecutor(max_payload_bytes=DEFAULT_MAX_PAYLOAD_BYTES)

        self._connection = ConnectionExecutor(
            transport=self._transport,
            config=self._connection_config,
        )

        self._maintenance = MaintenanceExecutor(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=16.0,
        )

        self._scene_queue = SceneQueueExecutor(
            transport=self._transport,
            max_depth=DEFAULT_MAX_DEPTH,
            wait_timeout_seconds=30.0,
        )

        self._code_executor = CodeExecutionExecutor(
            security_policy=code_validation,
            transport=self._transport,
            max_output_bytes=DEFAULT_MAX_OUTPUT_BYTES,
            execution_timeout_seconds=DEFAULT_EXECUTION_TIMEOUT_SECONDS,
        )

        self._orchestrator = GatewayOrchestrator(
            connection=self._connection,
            maintenance=self._maintenance,
            transport=self._transport,
            scene_queue=self._scene_queue,
            code_executor=self._code_executor,
            launcher=self._launcher,
        )

        self._maintenance._reconnect_fn = self._orchestrator.reconnect_with_runtime

    @property
    def agent(self) -> IGatewayAggregate:
        return self._orchestrator

    def get_orchestrator(self) -> IGatewayAggregate:
        return self._orchestrator


def create_gateway_feature(
    launcher: ILauncherOperateAggregate | None = None,
    connection_config: ConnectionConfigVO | None = None,
    code_validation: CodeValidationProtocol | None = None,
) -> IGatewayAggregate:
    """Factory function to create the gateway orchestrator."""
    container = GatewayContainer(
        launcher=launcher,
        connection_config=connection_config,
        code_validation=code_validation,
    )
    return container.get_orchestrator()
