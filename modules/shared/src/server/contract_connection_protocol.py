"""Contract: Protocol for Blender connection lifecycle management.

Implemented by Capabilities that handle TCP/stdio connection,
heartbeat monitoring, auto-reconnect, and status reporting.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ActionName, Details
from .taxonomy_server_error import (
    AuthenticationError,
    BlenderConnectionExhausted,
    ConnectionClosedError,
    ConnectionConfigError,
    ProtocolVersionMismatchError,
)
from .taxonomy_server_event import ConnectionEstablished, ConnectionLost
from .taxonomy_server_vo import CommandResult, ConnectionConfig, ConnectionStatus


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
                 ProtocolVersionMismatchError, or BlenderConnectionExhausted
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
        command_type: ActionName,
        params: Details | None = None,
    ) -> CommandResult:
        """Send a command to Blender and return the parsed response.

        Success: Returns CommandResult with status='success', data from JSON response
        Failure: Raises ConnectionClosedError, AuthenticationError, or ProtocolVersionMismatchError
        Event: CommandDispatched(action=str(command_type), execution_time_ms)
        """
        ...

    @abstractmethod
    async def receive_full_response(
        self,
        buffer_size: int = 8192,
    ) -> bytes:
        """Receive complete JSON response from socket in chunks.

        Success: Returns raw bytes of the JSON response
        Failure: Raises ConnectionClosedError if connection dropped during receive
        Event: None (infrastructure-level detail)
        """
        ...
