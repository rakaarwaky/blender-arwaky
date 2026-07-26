"""SocketClient: TCP communication with Blender addon."""

import json
import socket
import struct
from typing import Any

MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_TIMEOUT = 30.0


class BlenderSocketClient:
    """TCP client for communicating with Blender addon."""

    def __init__(self, host: str = "localhost", port: int = 9876, timeout: float = DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None

    def connect(self) -> None:
        """Connect to Blender addon."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.timeout)
        self._sock.connect((self.host, self.port))

    def disconnect(self) -> None:
        """Disconnect from Blender addon."""
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def send_command(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a command to Blender and return the response.

        Args:
            action: Command type (e.g., "execute_code", "get_scene_info")
            params: Command parameters

        Returns:
            Response dict from Blender addon
        """
        if not self._sock:
            raise ConnectionError("Not connected to Blender")

        command = {"type": action, "params": params or {}}

        # Send with length prefix
        data = json.dumps(command).encode("utf-8")
        header = struct.pack("!I", len(data))
        self._sock.sendall(header + data)

        # Receive response
        return self._receive_response()

    def _receive_response(self) -> dict[str, Any]:
        """Receive a length-prefixed JSON response."""
        if not self._sock:
            raise ConnectionError("Not connected to Blender")

        # Read 4-byte length header
        header = self._recv_exact(4)
        msg_len = struct.unpack("!I", header)[0]

        if msg_len > MAX_MESSAGE_SIZE:
            raise ValueError(f"Response too large: {msg_len} bytes")

        # Read message body
        body = self._recv_exact(msg_len)
        return json.loads(body.decode("utf-8"))

    def _recv_exact(self, n: int) -> bytes:
        """Receive exactly n bytes."""
        if not self._sock:
            raise ConnectionError("Not connected to Blender")

        data = b""
        while len(data) < n:
            chunk = self._sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data

    def __enter__(self) -> "BlenderSocketClient":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()
