"""Capability: Blender command dispatch and framed transport.

FR-GWY-003: Transport Request and Response
- Every request carries unique tracking ID
- Every response is correlated back through tracking ID
- Enforces payload size limits and transport timeout
- Discards uncorrelated/orphan responses safely

Contains BlenderCommandAdapter (asyncio-based, IBlenderCommandProtocol)
and TransportExecutor (sync socket-based, TransportProtocol).
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import time
import uuid

from modules.diagnostics.src.contract_audit_emission_protocol import (
    IEventPublisher,
)
from modules.shared.src.gateway.contract_connection_protocol import (
    IBlenderConnectionProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    IBlenderCommandProtocol,
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    CommandTimeoutError,
    PayloadLimitError,
    ProviderError,
    TimeoutError,
    TransportParseError,
    ValidationError,
)
from modules.shared.src.gateway.taxonomy_gateway_event import (
    CommandDispatched,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CommandResult,
    TransportMessageVO,
    TransportOutcomeVO,
)
from modules.shared.src.gateway.utility.utility_schema import (
    effective_command_timeout_ms,
    get_command_spec,
    validate_command_args,
)

logger = logging.getLogger("BlenderMCPServer")


class BlenderCommandAdapter(IBlenderCommandProtocol):
    """Command dispatch capability for Blender TCP/stdio operations.

    Implements FR-SRV-003 (v2.0.0): dispatches named commands with
    catalog-driven validation, timeout enforcement, and response
    truncation. No queue management — queued by orchestrator.
    """

    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        event_publisher: IEventPublisher,
        max_command_response_bytes: int = 1_048_576,
    ) -> None:
        self._connection = connection_port
        self._event_publisher = event_publisher
        self._max_response_bytes = max_command_response_bytes

    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: str | None = None,
    ) -> CommandResult:
        get_command_spec(action)
        try:
            validate_command_args(action, params)
        except ValidationError:
            raise
        effective_timeout = effective_command_timeout_ms(action, timeout_ms)
        timeout_s = effective_timeout / 1000.0
        start = time.monotonic()
        try:
            result = await asyncio.wait_for(
                self._connection.send_command(
                    action=action,
                    params=params,
                    request_id=request_id,
                    timeout_ms=effective_timeout,
                ),
                timeout=timeout_s,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            if result.data is not None:
                data_bytes = len(result.data.encode("utf-8")) if isinstance(result.data, str) else len(result.data)
                if data_bytes > self._max_response_bytes:
                    if isinstance(result.data, str):
                        result.data = result.data[:self._max_response_bytes] + "\n...[truncated]"
                    result.truncated = True
            logger.info("Command %s completed in %.1fms", action, elapsed_ms)
            await self._event_publisher.publish(
                CommandDispatched(action=action, execution_time_ms=elapsed_ms)
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("Command %s timed out after %.1fms", action, timeout_s * 1000)
            raise CommandTimeoutError(action=action, timeout_ms=effective_timeout) from None
        except ValidationError:
            raise
        except ProviderError:
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            raise ProviderError(
                message=f"Command '{action}' failed: {e}",
                details={"action": action},
            )


class TransportExecutor(TransportProtocol):
    """Concrete implementation for framed request/response transport.

    FR-GWY-003: Length-prefixed framing, UTF-8 encoding, tracking correlation.
    Enforces payload limits and per-request timeout.
    """

    def __init__(self, max_payload_bytes: int = 10_485_760) -> None:
        self._socket: socket.SocketType | None = None
        self._max_payload_bytes: int = max_payload_bytes
        self._pending_tracking_ids: dict[str, bool] = {}

    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
        if not request.tracking_id:
            request = TransportMessageVO(
                tracking_id=str(uuid.uuid4()),
                operation_class=request.operation_class,
                payload=request.payload,
                timeout_override_seconds=request.timeout_override_seconds,
            )
        if request.payload and len(request.payload) > self._max_payload_bytes:
            raise PayloadLimitError(
                f"Request payload {len(request.payload)} bytes exceeds limit {self._max_payload_bytes}"
            )
        start_time = time.time()
        self._pending_tracking_ids[request.tracking_id] = True
        try:
            frame = self._create_frame(request)
            timeout = request.timeout_override_seconds or 30.0
            if self._socket:
                self._socket.settimeout(timeout)
                self._socket.sendall(frame)
            response_data = self._receive_response(timeout)
            duration_ms = (time.time() - start_time) * 1000
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
            return TransportOutcomeVO(
                tracking_id=request.tracking_id,
                status="error",
                error=str(e),
            )

    def _create_frame(self, request: TransportMessageVO) -> bytes:
        message = json.dumps({
            "tracking_id": request.tracking_id,
            "operation_class": request.operation_class,
            "payload": (request.payload or b"").hex() if request.payload else None,
        })
        encoded = message.encode("utf-8")
        return len(encoded).to_bytes(4, "big") + encoded

    def _receive_response(self, timeout_seconds: float) -> bytes:
        if not self._socket:
            raise TimeoutError("No socket connection")
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

    def _parse_response(self, data: bytes, expected_tracking_id: str) -> TransportOutcomeVO:
        try:
            message = json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise TransportParseError(f"Failed to parse response: {e}")
        if message.get("tracking_id") != expected_tracking_id:
            logger.warning(
                "Orphan response discarded: expected=%s, got=%s",
                expected_tracking_id, message.get("tracking_id"),
            )
        return TransportOutcomeVO(
            tracking_id=message.get("tracking_id", ""),
            status=message.get("status", "error"),
            payload=(message.get("payload") or "").encode("hex") if message.get("payload") else None,
        )

    def set_socket(self, sock: socket.SocketType) -> None:
        self._socket = sock

    def __repr__(self) -> str:
        return f"TransportExecutor(max_payload={self._max_payload_bytes}, pending={len(self._pending_tracking_ids)})"
