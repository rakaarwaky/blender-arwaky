"""Root layer: Dependency injection container for the server feature.

Wires capabilities → agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured IBlenderServerAggregate.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from modules.shared.src.server import (
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    ICodeExecutionProtocol,
    IExecutionQueueProtocol,
    ITaskManagerProtocol,
)
from modules.shared.src.server import (
    QueueConfig,
    TaskManagerConfig,
)

# Lazy imports to avoid circular deps at module load time
if TYPE_CHECKING:
    from .agent_server_orchestrator import ServerOrchestrator
    from .capabilities_blender_command_adapter import BlenderCommandAdapter
    from .capabilities_blender_connection import BlenderConnection, BlenderConnectionFactory
    from .capabilities_code_execution_adapter import CodeExecutionAdapter
    from .capabilities_server_queue import ExecutionQueue
    from .capabilities_server_task_manager import TaskManager

logger = logging.getLogger("BlenderMCPServer")


class ServerContainer:
    """DI container that wires server capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared connection management.
    All components are lazy-instantiated on first access.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9876,
        queue_config: QueueConfig | None = None,
        task_config: TaskManagerConfig | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._queue_config = queue_config or QueueConfig()
        self._task_config = task_config or TaskManagerConfig()
        self._lock = threading.Lock()
        self._connection: IBlenderConnectionProtocol | None = None
        self._aggregate: IBlenderServerAggregate | None = None

    # ─── Block 2: Container Wiring & Accessors ──────────────

    def _build_connection(self) -> IBlenderConnectionProtocol:
        """Build and return the Blender connection capability."""
        conn = BlenderConnection(host=self._host, port=self._port)
        logger.info("Created connection to %s:%d", self._host, self._port)
        return conn

    def _build_command_adapter(
        self,
        connection: IBlenderConnectionProtocol,
    ) -> IBlenderCommandProtocol:
        """Build command dispatch capability."""
        return BlenderCommandAdapter(connection)

    def _build_code_executor(
        self,
        connection: IBlenderConnectionProtocol,
    ) -> ICodeExecutionProtocol:
        """Build code execution capability with AST validation."""
        return CodeExecutionAdapter(connection)

    def _build_queue(self) -> IExecutionQueueProtocol:
        """Build serialized execution queue."""
        return ExecutionQueue(config=self._queue_config)

    def _build_task_manager(self) -> ITaskManagerProtocol:
        """Build async task lifecycle manager."""
        return TaskManager(config=self._task_config)

    def get_aggregate(self) -> IBlenderServerAggregate:
        """Return a fully wired ServerOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.
        """
        if self._aggregate is not None:
            return self._aggregate

        with self._lock:
            # Double-check after lock acquisition
            if self._aggregate is not None:
                return self._aggregate

            connection = self._build_connection()
            self._connection = connection

            queue = self._build_queue()
            task_manager = self._build_task_manager()
            code_executor = self._build_code_executor(connection)
            command_adapter = self._build_command_adapter(connection)

            from .agent_server_orchestrator import ServerOrchestrator

            self._aggregate = ServerOrchestrator(
                connection=connection,
                code_executor=code_executor,
                queue=queue,
                task_manager=task_manager,
            )

        logger.info("Server container fully wired")
        return self._aggregate

    def get_connection(self) -> IBlenderConnectionProtocol:
        """Return the shared Blender connection (singleton)."""
        if self._connection is None:
            with self._lock:
                if self._connection is None:
                    self._connection = self._build_connection()
        return self._connection

    def shutdown(self) -> None:
        """Gracefully shut down all server components."""
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.disconnect()
                except Exception as e:
                    logger.warning("Error during connection shutdown: %s", e)
                self._connection = None
            self._aggregate = None

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return f"ServerContainer(host={self._host!r}, port={self._port})"


def create_container(
    host: str = "localhost",
    port: int = 9876,
) -> ServerContainer:
    """Factory function to create a new server container.

    Convenience wrapper for developers who don't need custom config.

    Args:
        host: Blender addon host address.
        port: Blender addon TCP port.

    Returns:
        Configured ServerContainer instance.
    """
    return ServerContainer(host=host, port=port)
