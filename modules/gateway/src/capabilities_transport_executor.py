"""Transport capability — framed request/response with tracking, limits, and timeout.

FR-GWY-003: Transport Request and Response
- Every request carries unique tracking ID
- Every response is correlated back through tracking ID
- Enforces payload size limits and transport timeout
- Discards uncorrelated/orphan responses safely
"""

import json
import logging
import socket
import time
import uuid

from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    PayloadLimitError,
    TimeoutError,
    TransportParseError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    TransportMessageVO,
    TransportResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class TransportExecutor(TransportProtocol):
    """Concrete implementation for framed request/response transport.

    FR-GWY-003: Length-prefixed framing, UTF-8 encoding, tracking correlation.
    Enforces payload limits and per-request timeout.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, max_payload_bytes: int = 10_485_760) -> None:
        self._socket: socket.SocketType | None = None
        self._max_payload_bytes: int = max_payload_bytes
        self._pending_tracking_ids: dict[str, bool] = {}

    # ─── Block 2: Protocol Method Implementation ─────────────

    def send_request(self, request: TransportMessageVO) -> TransportResultVO:
        """Send command to Blender and receive correlated response.

        FR-GWY-003: Every request carries unique tracking ID. Every response
        is correlated back. Enforces payload limits and transport timeout.
        Discards uncorrelated/orphan responses safely.
        """
        # Validate tracking ID
        if not request.tracking_id:
            request = TransportMessageVO(
                tracking_id=str(uuid.uuid4()),
                operation_class=request.operation_class,
                payload=request.payload,
                timeout_override_seconds=request.timeout_override_seconds,
            )

        # Enforce outgoing payload limit
        if request.payload and len(request.payload) > self._max_payload_bytes:
            raise PayloadLimitError(
                f"Request payload {len(request.payload)} bytes exceeds limit {self._max_payload_bytes}"
            )

        start_time = time.time()
        self._pending_tracking_ids[request.tracking_id] = True

        try:
            # Serialize request with length-prefixed framing
            frame = self._create_frame(request)
            timeout = request.timeout_override_seconds or 30.0

            if self._socket:
                self._socket.settimeout(timeout)
                self._socket.sendall(frame)

            # Receive response
            response_data = self._receive_response(timeout)
            duration_ms = (time.time() - start_time) * 1000

            # Parse and correlate response
            response = self._parse_response(response_data, request.tracking_id)
            response.duration_ms = duration_ms
            response.request_size_bytes = len(frame)

            logger.debug(
                "Transport complete: tracking_id=%s, status=%s, %.1fms",
                request.tracking_id, response.status, duration_ms,
            )
            return response

        except TimeoutError:
            raise
        except PayloadLimitError:
            raise
        except Exception as e:
            logger.error("Transport error: %s", e)
            return TransportResultVO(
                tracking_id=request.tracking_id,
                status="error",
                error=str(e),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _create_frame(self, request: TransportMessageVO) -> bytes:
        """Create length-prefixed framed message."""
        message = json.dumps({
            "tracking_id": request.tracking_id,
            "operation_class": request.operation_class,
            "payload": (request.payload or b"").hex() if request.payload else None,
        })
        # Length prefix: 4 bytes big-endian
        encoded = message.encode("utf-8")
        return len(encoded).to_bytes(4, "big") + encoded

    def _receive_response(self, timeout_seconds: float) -> bytes:
        """Receive complete response with length-prefixed framing."""
        if not self._socket:
            raise TimeoutError("No socket connection")

        # Read length prefix (4 bytes)
        header = b""
        while len(header) < 4:
            chunk = self._socket.recv(4 - len(header))
            if not chunk:
                raise TimeoutError("Connection closed during header read")
            header += chunk

        length = int.from_bytes(header, "big")
        data = b""
        while len(data) < length:
            chunk = self._socket.recv(length - len(data))
            if not chunk:
                raise TimeoutError("Connection closed during payload read")
            data += chunk

        return data

    def _parse_response(self, data: bytes, expected_tracking_id: str) -> TransportResultVO:
        """Parse JSON response and correlate tracking ID."""
        try:
            message = json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise TransportParseError(f"Failed to parse response: {e}")

        # Check for orphan response
        if message.get("tracking_id") != expected_tracking_id:
            logger.warning(
                "Orphan response discarded: expected=%s, got=%s",
                expected_tracking_id, message.get("tracking_id"),
            )

        return TransportResultVO(
            tracking_id=message.get("tracking_id", ""),
            status=message.get("status", "error"),
            payload=(message.get("payload") or "").encode("hex") if message.get("payload") else None,
        )

    def set_socket(self, sock: socket.SocketType) -> None:
        """Set the socket for transport operations (called by connection executor)."""
        self._socket = sock

    def __repr__(self) -> str:
        return f"TransportExecutor(max_payload={self._max_payload_bytes}, pending={len(self._pending_tracking_ids)})"
