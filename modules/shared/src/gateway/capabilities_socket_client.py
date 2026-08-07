"""TCP socket client — CLI ↔ Blender addon communication.

Shared utility between CLI surface and gateway feature.
Length-prefixed JSON transport for command/response pattern.
"""

import contextlib
import json
import socket
import struct
from typing import Any

from modules.shared.src.gateway.contract_transport_protocol import TransportProtocol
from modules.shared.src.gateway.taxonomy_gateway_vo import TransportMessageVO, TransportOutcomeVO

MAX_MESSAGE_SIZE = 10 * 1024 * 1024
DEFAULT_TIMEOUT = 30.0


class BlenderSocketClient(TransportProtocol):
    """TCP client for communicating with Blender addon."""

    def __init__(self, host: str = "localhost", port: int = 9876, timeout: float = DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None

    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
        """Send a framed transport request and return the correlated outcome."""
        if not self._sock:
            self.connect()
        params = json.loads(request.payload.decode("utf-8")) if request.payload else {}
        response = self.send_command(request.operation_class, params)
        outcome_payload = json.dumps(response).encode("utf-8")
        return TransportOutcomeVO(
            tracking_id=request.tracking_id,
            status="success",
            payload=outcome_payload,
            request_size_bytes=len(request.payload or b""),
            response_size_bytes=len(outcome_payload),
        )

    def connect(self) -> None:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.timeout)
            self._sock.connect((self.host, self.port))
        except TimeoutError as err:
            raise ConnectionError(f"Connection to {self.host}:{self.port} timed out ({self.timeout}s)") from err
        except ConnectionRefusedError as e:
            raise ConnectionError(f"Connection refused at {self.host}:{self.port}") from e
        except OSError as e:
            raise ConnectionError(f"Network error connecting to {self.host}:{self.port}: {e}") from e

    def disconnect(self) -> None:
        if self._sock:
            with contextlib.suppress(Exception):
                self._sock.close()
            self._sock = None

    def send_command(self, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._sock:
            raise ConnectionError("Not connected to Blender")
        command = {"type": action, "params": params or {}}
        try:
            data = json.dumps(command).encode("utf-8")
            header = struct.pack("!I", len(data))
            self._sock.sendall(header + data)
        except OSError as e:
            raise ConnectionError(f"Failed to send command: {e}") from e
        return self._receive_response()

    def _receive_response(self) -> dict[str, Any]:
        if not self._sock:
            raise ConnectionError("Not connected to Blender")
        header = self._recv_exact(4)
        msg_len = struct.unpack("!I", header)[0]
        if msg_len > MAX_MESSAGE_SIZE:
            raise ValueError(f"Response too large: {msg_len} bytes")
        body = self._recv_exact(msg_len)
        return json.loads(body.decode("utf-8"))

    def _recv_exact(self, n: int) -> bytes:
        if not self._sock:
            raise ConnectionError("Not connected to Blender")
        data = b""
        while len(data) < n:
            try:
                chunk = self._sock.recv(n - len(data))
            except OSError as e:
                raise ConnectionError(f"Receive error after {len(data)}/{n} bytes: {e}") from e
            if not chunk:
                raise ConnectionError("Connection closed prematurely")
            data += chunk
        return data

    def __enter__(self) -> "BlenderSocketClient":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()
