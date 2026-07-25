"""Root: Server feature container.

Wires capabilities to contracts and aggregate. Connects
BlenderConnection, CodeExecutionAdapter, and BlenderSocketAdapter
to their protocol contracts and the ServerOrchestrator aggregate.
"""

from __future__ import annotations

import logging

from modules.shared.src.server import (
    ConnectionConfig,
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
)
from modules.server.src.capabilities_blender_connection import BlenderConnection, BlenderConnectionFactory
from modules.server.src.capabilities_code_execution_adapter import CodeExecutionAdapter
from modules.server.src.agent_server_orchestrator import ServerOrchestrator
from modules.server.src.surface_socket_command import BlenderSocketCommandSurface

logger = logging.getLogger("BlenderMCPServer")


class ServerContainer:
    """Composition root for the server feature.

    Wires capabilities to protocol contracts and creates
    the aggregate facade for the surface layer.
    """

    def __init__(self, config: ConnectionConfig | None = None) -> None:
        self._config = config or ConnectionConfig(transport_type="socket")
        self._connection: IBlenderConnectionProtocol | None = None
        self._code_executor: ICodeExecutionProtocol | None = None
        self._orchestrator: ServerOrchestrator | None = None
        self._surface: BlenderSocketCommandSurface | None = None

    def wire(self) -> BlenderSocketCommandSurface:
        """Wire all dependencies and return the surface entry point."""
        # Create capabilities
        self._connection = BlenderConnection(
            host=self._config.host,
            port=self._config.port,
        )
        self._code_executor = CodeExecutionAdapter(self._connection)

        # Create agent (aggregate)
        self._orchestrator = ServerOrchestrator(
            connection=self._connection,
            code_executor=self._code_executor,
        )

        # Create surface
        self._surface = BlenderSocketCommandSurface(self._orchestrator)

        logger.info("Server container wired successfully")
        return self._surface

    @property
    def surface(self) -> BlenderSocketCommandSurface:
        """Get the surface entry point. Must call wire() first."""
        if self._surface is None:
            raise RuntimeError("Container not wired. Call wire() first.")
        return self._surface

    @property
    def orchestrator(self) -> ServerOrchestrator:
        """Get the orchestrator aggregate."""
        if self._orchestrator is None:
            raise RuntimeError("Container not wired. Call wire() first.")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shutdown all wired components."""
        if self._connection:
            self._connection.disconnect()
        logger.info("Server container shut down")
