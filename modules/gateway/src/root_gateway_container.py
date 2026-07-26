"""Root layer: Dependency injection container for the server feature.

Wires capabilities → agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured IBlenderServerAggregate.
Implements v2.0.0 configuration loading from file, env, and programmatic overrides.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.gateway.src import (
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    ICodeExecutionProtocol,
    IMetricsProvider,
    ServerConfig,
    load_server_config,
)

logger = logging.getLogger("BlenderMCPServer")


class GatewayContainer:
    """DI container that wires server components per v2.0.0 architecture.

    Accepts ServerConfig, builds event bus → metrics → queue → connection
    → command adapter → code executor → orchestrator in dependency order.
    Provides async start/shutdown lifecycle.
    """

    def __init__(self, config: ServerConfig | None = None) -> None:
        """Initialize container with optional config.

        If config is None, loads from file/env/defaults via load_server_config().

        Args:
            config: Optional ServerConfig. Falls back to load_server_config().
        """
        self._config = config or load_server_config()
        self._aggregate: IBlenderServerAggregate | None = None
        self._event_bus: Any = None  # InMemoryEventBus
        self._metrics: IMetricsProvider | None = None

    # ─── Block 2: Container Wiring ─────────────────────────────

    async def start(self) -> IBlenderServerAggregate:
        """Build all components and start the server.

        Returns:
            Fully wired IBlenderServerAggregate implementation.

        Raises:
            RuntimeError: If already started.
        """
        if self._aggregate is not None:
            return self._aggregate

        # 1. Build event bus
        from modules.gateway.src.capabilities_event_bus import InMemoryEventBus
        self._event_bus = InMemoryEventBus()

        # 2. Build metrics collector and subscribe to event bus
        from modules.gateway.src.capabilities_metrics_collector import MetricsCollector
        self._metrics = MetricsCollector()
        self._event_bus.subscribe(self._metrics)

        # 3. Build connection
        conn = self._build_connection(self._event_bus)

        # 4. Build operation queue
        from modules.gateway.src.capabilities_operation_queue import OperationQueue
        queue = OperationQueue(
            event_publisher=self._event_bus,
            max_depth=self._config.queue_max_depth,
            wait_timeout_ms=self._config.queue_wait_timeout_ms,
        )

        # 5. Build command adapter
        cmd_adapter = self._build_command_adapter(conn, self._event_bus)

        # 6. Build code executor
        code_exec = self._build_code_executor(conn, self._event_bus)

        # 7. Build orchestrator
        from modules.gateway.src.agent_gateway_orchestrator import GatewayOrchestrator
        self._aggregate = GatewayOrchestrator(
            connection=conn,
            code_executor=code_exec,
            command_adapter=cmd_adapter,
            operation_queue=queue,
            event_publisher=self._event_bus,
            metrics_provider=self._metrics,
            queue_wait_timeout_ms=self._config.queue_wait_timeout_ms,
            execution_default_timeout_ms=self._config.execution_default_timeout_ms,
        )

        # 8. Start orchestrator (starts queue worker)
        await self._aggregate.start()

        logger.info("Server container fully wired and started")
        return self._aggregate

    async def shutdown(self) -> None:
        """Gracefully shut down all components."""
        if self._aggregate is not None:
            try:
                await self._aggregate.shutdown()
            except Exception as e:
                logger.warning("Error during shutdown: %s", e)
            self._aggregate = None

    def _build_connection(self, event_publisher: Any) -> IBlenderConnectionProtocol:
        """Build the Blender connection capability."""
        from modules.gateway.src.capabilities_blender_connection import BlenderConnection
        return BlenderConnection(event_publisher=event_publisher)

    def _build_command_adapter(
        self,
        connection: IBlenderConnectionProtocol,
        event_publisher: Any,
    ) -> IBlenderCommandProtocol:
        """Build command dispatch capability."""
        from modules.gateway.src.capabilities_blender_command_adapter import BlenderCommandAdapter
        return BlenderCommandAdapter(
            connection_port=connection,
            event_publisher=event_publisher,
            max_command_response_bytes=self._config.max_command_response_bytes,
        )

    def _build_code_executor(
        self,
        connection: IBlenderConnectionProtocol,
        event_publisher: Any,
    ) -> ICodeExecutionProtocol:
        """Build code execution capability with centralized validation."""
        from modules.gateway.src import CodeSecurityPolicy
        from modules.gateway.src.capabilities_code_execution_adapter import CodeExecutionAdapter

        return CodeExecutionAdapter(
            connection_port=connection,
            event_publisher=event_publisher,
            security_policy=CodeSecurityPolicy(
                allowed_directories=self._config.allowed_directories,
                max_payload_bytes=self._config.max_code_payload_bytes,
            ),
            task_config=None,  # Default config
            default_timeout_ms=self._config.execution_default_timeout_ms,
            max_output_bytes=self._config.max_execution_output_bytes,
        )

    def get_aggregate(self) -> IBlenderServerAggregate:
        """Return the wired aggregate (must call start() first)."""
        if self._aggregate is None:
            raise RuntimeError("GatewayContainer not started. Call start() first.")
        return self._aggregate

    def __repr__(self) -> str:
        return f"GatewayContainer(host={self._config.host!r}, port={self._config.port})"


def create_container(
    config_path: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> GatewayContainer:
    """Factory function to create a new server container.

    Loads config from file/env/defaults and creates the container.

    Args:
        config_path: Path to YAML config file. Falls back to BLENDERMCP_CONFIG_PATH.
        overrides: Programmatic key-value overrides.

    Returns:
        Configured GatewayContainer instance.
    """
    config = load_server_config(config_path=config_path, overrides=overrides)
    return GatewayContainer(config=config)
