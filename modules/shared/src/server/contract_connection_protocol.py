"""Contract: Protocol for Blender connection lifecycle management.

Implemented by Capabilities that handle TCP/stdio connection,
heartbeat monitoring, auto-reconnect, and status reporting.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ActionName, Details, SuccessFlag


class IBlenderConnectionProtocol(ABC):
    """Protocol for Blender TCP/stdio connection lifecycle."""

    @abstractmethod
    async def connect(self) -> SuccessFlag:
        """Establish connection to Blender with retries and handshake.

        Performs TCP connection with exponential backoff retry,
        protocol version validation, and authentication when enabled.
        Returns SuccessFlag (True if successful).
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection gracefully. Must be idempotent."""
        ...

    @abstractmethod
    async def is_connected(self) -> SuccessFlag:
        """Check if socket is currently connected and alive."""
        ...

    @abstractmethod
    async def send_command(
        self, command_type: ActionName, params: Details | None = None
    ) -> Details:
        """Send a command to Blender and return the JSON response.

        Serializes command as JSON, sends over TCP, receives and
        parses response. Raises BlenderConnectionFailure on errors.
        """
        ...

    @abstractmethod
    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        """Receive complete JSON response from socket in chunks.

        Args:
            buffer_size: Size of receive buffer in bytes (default: 8192).

        Returns:
            Complete raw bytes of the JSON response.
        """
        ...
