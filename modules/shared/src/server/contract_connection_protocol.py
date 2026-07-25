"""Contract: Protocol for Blender connection lifecycle management.

Implemented by Capabilities that handle TCP/stdio connection,
heartbeat monitoring, auto-reconnect, and status reporting.
AES Protocol layer — depends only on Taxonomy.
"""

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_server_vo import ConnectionConfig, ConnectionStatus


class IBlenderConnectionProtocol(ABC):
    """Protocol for Blender TCP/stdio connection lifecycle."""

    @abstractmethod
    def connect(self, host: str = "localhost", port: int = 9876) -> Any:
        """Establish connection to Blender with retries and handshake.

        Performs TCP connection with exponential backoff retry,
        protocol version validation, and authentication when enabled.
        Returns SuccessFlag (True if successful).
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection gracefully. Must be idempotent."""
        pass

    @abstractmethod
    def is_connected(self) -> Any:
        """Check if socket is currently connected and alive."""
        pass

    @abstractmethod
    def send_command(self, command_type: Any, params: dict | None = None) -> dict:
        """Send a command to Blender and return the JSON response.

        Serializes command as JSON, sends over TCP, receives and
        parses response. Raises BlenderConnectionFailure on errors.
        """
        pass

    @abstractmethod
    def receive_full_response(self, sock: Any, buffer_size: int = 8192) -> bytes:
        """Receive complete JSON response from socket in chunks."""
        pass
