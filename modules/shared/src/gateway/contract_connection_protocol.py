"""Gateway domain contract: connection protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-GWY-001: Establish Connection to Blender.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import (
    CommandResult,
    ConnectionConfig,
    ConnectionOutcomeVO,
    ConnectionStatus,
)


class ConnectionProtocol(ABC):
    """Protocol interface for establishing and managing transport connection."""

    @abstractmethod
    def establish_connection(self) -> ConnectionOutcomeVO:
        """Establish transport channel to Blender with handshake and protocol check.

        FR-GWY-001: Idempotent when already connected. Validates protocol version.
        Rejects incompatible versions. Transports auth material only when enabled.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Graceful disconnect. Must be idempotent.

        FR-GWY-002: State transitions to closed. No-op if already disconnected.
        """
        ...


class IBlenderConnectionProtocol(ABC):
    """Protocol for Blender TCP/stdio connection lifecycle.

    All methods use explicit typed errors — no bare strings.
    Query methods return bool or typed results; command methods raise on failure.
    """

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection to Blender with retries and handshake.

        Success: Returns ConnectionStatus with state='connected'
        Failure: Raises ConnectionConfigError, AuthenticationError,
                 VersionMismatchError, or BlenderConnectionExhaustedError
        Event: ConnectionEstablished(host, port, transport_type)
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Graceful disconnect. Must be idempotent.

        Success: No return; connection state becomes 'closed'
        Failure: Raises ConnectionClosedError (non-fatal, ignored by caller)
        Event: ConnectionLost(reason='closed')
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if socket is currently connected and alive.

        Success: Returns True if connected, False otherwise
        Failure: Raises ConnectionClosedError (connection dropped between checks)
        Event: ConnectionLost(reason='timeout') if connection timed out
        """
        ...

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        request_id: str | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        """Send a command to Blender and return the parsed response.

        Success: Returns CommandResult with status='success'
        Failure: Raises ConnectionClosedError, AuthenticationError, or VersionMismatchError
        Event: CommandDispatched(action, execution_time_ms)
        """
        ...

    @abstractmethod
    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        """Receive complete JSON response from socket in chunks.

        Success: Returns raw bytes of the JSON response
        Failure: Raises ConnectionClosedError if connection dropped during receive
        Event: None (infrastructure-level detail)
        """
        ...

    @abstractmethod
    def set_active_operation_in_progress(self, active: bool) -> None:
        """Mark whether an operation is currently running on this connection.

        Used by the orchestrator to coordinate heartbeat reconnection logic.
        When True, heartbeat will not trigger reconnect while operation runs.
        """
        ...
