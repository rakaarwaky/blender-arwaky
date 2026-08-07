"""Capability: Blender connection lifecycle — asyncio and sync implementations.

FR-GWY-001: Establish Connection
- Opens socket or stdio pipe channel
- Performs handshake and protocol version negotiation
- Authenticates when required
- Idempotent when already connected
- Delegates transport messaging to TransportProtocol
- Uses configured auth material for authentication

Contains BlenderConnection (asyncio stream-based, IBlenderConnectionProtocol)
and ConnectionExecutor (sync socket-based, ConnectionProtocol).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import socket as _socket
import struct
import time
import uuid
from contextlib import suppress

from modules.shared.src.gateway.contract_connection_protocol import (
    ConnectionProtocol,
    IBlenderConnectionProtocol,
)
from modules.shared.src.gateway.contract_event_protocol import (
    IEventPublisher,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_constant import (
    CONNECTION_STATE_CLOSED,
    CONNECTION_STATE_CONNECTED,
    CONNECTION_STATE_DISCONNECTED,
    CONNECTION_STATE_FAILED,
    CONNECTION_STATE_RECONNECTING,
    DEFAULT_PROTOCOL_VERSION,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    AuthenticationError,
    BlenderConnectionExhausted,
    BlenderConnectionFailure,
    ConnectionClosedError,
    ConnectionConfigError,
    TransportParseError,
    VersionMismatchError,
)
from modules.shared.src.gateway.taxonomy_gateway_event import (
    ConnectionEstablished,
    ConnectionLost,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CommandResult,
    ConnectionConfig,
    ConnectionConfigVO,
    ConnectionOutcomeVO,
    ConnectionState,
    ConnectionStatus,
    TransportMessageVO,
)

logger = logging.getLogger("BlenderMCPServer")


class BlenderConnection(IBlenderConnectionProtocol):
    """Asyncio-based persistent connection to Blender addon."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, event_publisher: IEventPublisher) -> None:
        self._event_publisher = event_publisher
        self._config: ConnectionConfig | None = None
        self._host: str = "localhost"
        self._port: int = 9876
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._state: ConnectionState = CONNECTION_STATE_DISCONNECTED
        self._active_operation: bool = False
        self._protocol_version: str | None = DEFAULT_PROTOCOL_VERSION
        self._last_error: str | None = None
        self._reconnect_attempts: int = 0
        self._session_id: str | None = None
        self._active_file_path: str | None = None
        self._active_directory: str | None = None
        self._last_heartbeat_at: float | None = None
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._consecutive_failures: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        self._config = config
        self._host = config.host or "localhost"
        self._port = config.port or 9876

        if config.require_auth_for_remote and self._is_remote() and not config.auth_token:
            raise ConnectionConfigError(
                message="Remote connection requires authentication token",
                details={"host": self._host},
            )

        max_attempts = config.reconnect_max_attempts
        base_delay = config.reconnect_base_delay_seconds
        max_delay = config.reconnect_max_delay_seconds

        for attempt in range(max_attempts):
            try:
                await self._establish_stream()
                await self._perform_handshake(config)
                await self._authenticate(config)

                self._state = CONNECTION_STATE_CONNECTED
                self._reconnect_attempts = attempt + 1
                self._consecutive_failures = 0
                self._last_heartbeat_at = time.monotonic()
                self._start_heartbeat(config)

                await self._event_publisher.publish(
                    ConnectionEstablished(
                        host=self._host,
                        port=self._port,
                        transport_type=config.transport_type,
                    )
                )

                status = ConnectionStatus(
                    state=CONNECTION_STATE_CONNECTED,
                    host=self._host,
                    port=self._port,
                    transport_type=config.transport_type,
                    protocol_version=self._protocol_version,
                    reconnect_attempts=self._reconnect_attempts,
                    session_id=self._session_id,
                    active_file_path=self._active_file_path,
                    active_directory=self._active_directory,
                )
                logger.info("Connected to Blender at %s:%d", self._host, self._port)
                return status

            except (VersionMismatchError, AuthenticationError, ConnectionConfigError):
                await self._close_stream()
                self._state = CONNECTION_STATE_FAILED
                raise

            except Exception as e:
                self._state = CONNECTION_STATE_FAILED
                self._last_error = str(e)
                logger.warning(
                    "Connection attempt %d/%d failed: %s",
                    attempt + 1,
                    max_attempts,
                    e,
                )
                await self._close_stream()
                if attempt < max_attempts - 1:
                    base = min(base_delay * (2**attempt), max_delay)
                    jitter = (time.monotonic() % 0.5) * base
                    delay = base + jitter
                    logger.debug("Waiting %.1f seconds before reconnect attempt %d", delay, attempt + 2)
                    await asyncio.sleep(delay)

        self._state = CONNECTION_STATE_FAILED
        raise BlenderConnectionExhausted(
            attempts=max_attempts,
            details={"host": self._host, "port": self._port},
        )

    async def disconnect(self) -> None:
        await self._stop_heartbeat()
        await self._close_stream()
        old_state = self._state
        self._state = CONNECTION_STATE_CLOSED
        if old_state != CONNECTION_STATE_CLOSED:
            await self._event_publisher.publish(ConnectionLost(reason="closed"))
            logger.info("Disconnected from Blender (state=%s)", CONNECTION_STATE_CLOSED)

    async def is_connected(self) -> bool:
        try:
            return not (self._writer is None or self._writer.closed)
        except Exception as e:
            logger.debug("is_connected check failed: %s", e)
            return False

    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        request_id: str | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        if self._writer is None or self._writer.closed:
            raise ConnectionClosedError(details={"reason": "no_writer"})
        try:
            payload = {
                "type": "command",
                "request_id": request_id or "",
                "action": action,
            }
            if params:
                payload["params"] = params
            json_bytes = json.dumps(payload).encode("utf-8")
            header = struct.pack("!I", len(json_bytes))
            try:
                self._writer.write(header + json_bytes)
                await self._writer.drain()
            except (BrokenPipeError, OSError) as e:
                raise ConnectionClosedError(details={"reason": "drain_failed", "error": str(e)}) from e
            response = await self._receive_response(timeout_ms)
            resp_dict = json.loads(response.decode("utf-8"))
            if resp_dict.get("status") == "error":
                raise BlenderConnectionFailure(
                    message=resp_dict.get("message", "Command failed"),
                    details={"action": action},
                )
            return CommandResult(
                status="success",
                data=resp_dict.get("result", {}),
                request_id=request_id,
            )
        except ConnectionClosedError:
            raise
        except Exception as e:
            if isinstance(e, (AuthenticationError, VersionMismatchError)):
                raise
            raise BlenderConnectionFailure(
                message=f"Command '{action}' failed: {e}",
                details={"action": action},
            ) from e

    async def receive_full_response(self, _buffer_size: int = 8192) -> bytes:
        if self._reader is None:
            raise ConnectionClosedError(details={"reason": "no_reader"})
        header = await self._reader.readexactly(4)
        msg_len = struct.unpack("!I", header)[0]
        payload = await self._reader.readexactly(msg_len)
        return payload

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def set_active_operation_in_progress(self, active: bool) -> None:
        self._active_operation = active

    def __repr__(self) -> str:
        return f"BlenderConnection(host={self._host!r}, port={self._port}, state={self._state})"

    async def _establish_stream(self) -> None:
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._config.connection_timeout_seconds,
            )
        except asyncio.TimeoutError:
            raise ConnectionConfigError(
                message=f"Connection to {self._host}:{self._port} timed out",
                details={"host": self._host, "port": self._port},
            ) from None

    async def _perform_handshake(self, config: ConnectionConfig) -> None:
        request_id = str(time.monotonic())
        payload = {
            "type": "handshake",
            "request_id": request_id,
            "protocol_version": config.protocol_version or DEFAULT_PROTOCOL_VERSION,
        }
        json_bytes = json.dumps(payload).encode("utf-8")
        header = struct.pack("!I", len(json_bytes))
        self._writer.write(header + json_bytes)
        await self._writer.drain()
        response = await self._receive_response()
        resp_dict = json.loads(response.decode("utf-8"))
        if resp_dict.get("status") == "version_mismatch":
            raise VersionMismatchError(
                expected=config.protocol_version or DEFAULT_PROTOCOL_VERSION,
                actual=resp_dict.get("protocol_version", ""),
            )
        if resp_dict.get("status") != "ok":
            raise ConnectionConfigError(
                message=f"Handshake failed: {resp_dict.get('message', 'unknown')}",
            )
        self._protocol_version = resp_dict.get("protocol_version", DEFAULT_PROTOCOL_VERSION)
        server_major = self._parse_major(config.protocol_version or DEFAULT_PROTOCOL_VERSION)
        addon_major = self._parse_major(self._protocol_version)
        if server_major != addon_major:
            raise VersionMismatchError(
                expected=config.protocol_version or DEFAULT_PROTOCOL_VERSION,
                actual=self._protocol_version,
            )
        self._session_id = resp_dict.get("result", {}).get("session_id")
        self._active_file_path = resp_dict.get("result", {}).get("active_file_path")
        self._active_directory = resp_dict.get("result", {}).get("active_directory")

    async def _authenticate(self, config: ConnectionConfig) -> None:
        if not config.auth_token:
            return
        token_hash = hashlib.sha256(config.auth_token.encode("utf-8")).hexdigest()
        payload = {
            "type": "auth",
            "request_id": str(time.monotonic()),
            "token_hash": token_hash,
        }
        json_bytes = json.dumps(payload).encode("utf-8")
        header = struct.pack("!I", len(json_bytes))
        self._writer.write(header + json_bytes)
        await self._writer.drain()
        try:
            response = await self._receive_response()
            resp_dict = json.loads(response.decode("utf-8"))
            if resp_dict.get("status") == "auth_failed":
                raise AuthenticationError(
                    message="Invalid authentication token",
                    details={"host": self._host},
                )
        except ConnectionClosedError:
            raise AuthenticationError(
                message="Authentication connection lost",
                details={"host": self._host},
            ) from None

    async def _receive_response(self, timeout_ms: float | None = None) -> bytes:
        timeout_s = timeout_ms / 1000.0 if timeout_ms else 30.0
        try:
            header = await asyncio.wait_for(self._reader.readexactly(4), timeout=timeout_s)
        except asyncio.TimeoutError:
            raise ConnectionClosedError(details={"reason": "response_timeout"}) from None
        except asyncio.IncompleteReadError:
            raise ConnectionClosedError(details={"reason": "connection_dropped"}) from None
        msg_len = struct.unpack("!I", header)[0]
        try:
            payload = await asyncio.wait_for(
                self._reader.readexactly(msg_len),
                timeout=timeout_s,
            )
        except asyncio.TimeoutError:
            raise ConnectionClosedError(details={"reason": "payload_timeout"}) from None
        except asyncio.IncompleteReadError:
            raise ConnectionClosedError(details={"reason": "connection_dropped_during_read"}) from None
        return payload

    def _is_remote(self) -> bool:
        return self._host not in ("localhost", "127.0.0.1", "::1")

    @staticmethod
    def _parse_major(version: str) -> int:
        try:
            return int(version.split(".")[0])
        except (IndexError, ValueError):
            return 0

    def _start_heartbeat(self, config: ConnectionConfig) -> None:
        interval = config.heartbeat_interval_seconds or 10
        threshold = config.heartbeat_failure_threshold or 3
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(interval, threshold))
        logger.debug("Heartbeat started (interval=%ds, threshold=%d)", interval, threshold)

    async def _stop_heartbeat(self) -> None:
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._heartbeat_task
            self._heartbeat_task = None

    async def _heartbeat_loop(self, interval: int, threshold: int) -> None:
        while True:
            try:
                await asyncio.sleep(interval)
                with suppress(ConnectionClosedError):
                    request_id = str(time.monotonic())
                    payload = {
                        "type": "ping",
                        "request_id": request_id,
                    }
                    json_bytes = json.dumps(payload).encode("utf-8")
                    header = struct.pack("!I", len(json_bytes))
                    self._writer.write(header + json_bytes)
                    await self._writer.drain()
                    with suppress(asyncio.TimeoutError, ConnectionClosedError):
                        response = await asyncio.wait_for(
                            self._receive_response(timeout_ms=5000),
                            timeout=5.0,
                        )
                        resp_dict = json.loads(response.decode("utf-8"))
                        if resp_dict.get("status") == "ok":
                            self._consecutive_failures = 0
                            self._last_heartbeat_at = time.monotonic()
                            continue
                self._consecutive_failures += 1
                logger.warning(
                    "Heartbeat failure %d/%d",
                    self._consecutive_failures,
                    threshold,
                )
                if self._consecutive_failures >= threshold:
                    if self._active_operation:
                        logger.warning("Operation in progress — deferring reconnect")
                        continue
                    self._state = CONNECTION_STATE_RECONNECTING
                    await self._event_publisher.publish(ConnectionLost(reason="heartbeat_timeout"))
                    await self._close_stream()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Heartbeat error: %s", e)
                self._consecutive_failures += 1

    async def _close_stream(self) -> None:
        if self._writer is not None and not self._writer.closed:
            with suppress(Exception):
                self._writer.close()
                await self._writer.wait_closed()
        self._reader = None
        self._writer = None


class ConnectionExecutor(ConnectionProtocol):
    """Concrete implementation for transport connection establishment."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        transport: TransportProtocol,
        config: ConnectionConfigVO | None = None,
    ) -> None:
        validated_config = config or ConnectionConfigVO()
        if not validated_config.host or not validated_config.port:
            raise ConnectionConfigError(
                message="ConnectionConfigVO requires host and port",
                details={"host": validated_config.host, "port": validated_config.port},
            )
        self._socket: _socket.SocketType | None = None
        self._transport: TransportProtocol = transport
        self._config: ConnectionConfigVO = validated_config
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self._protocol_version: str = ""
        self._endpoint_summary: str = ""
        self._capabilities: tuple[str, ...] = ()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def establish_connection(self) -> ConnectionOutcomeVO:
        if self._state == ConnectionState.CONNECTED:
            logger.info("Already connected — idempotent")
            return ConnectionOutcomeVO(
                state=ConnectionState.CONNECTED,
                protocol_version=self._protocol_version,
                transport_type=self._config.transport_type,
                endpoint_summary=f"{self._config.host}:{self._config.port}",
                capabilities=self._capabilities,
            )

        start_time = time.time()
        self._state = ConnectionState.CONNECTING
        logger.info("Establishing connection to %s:%d", self._config.host, self._config.port)

        sock: _socket.SocketType | None = None
        try:
            timeout = self._config.timeout_seconds or 30.0
            sock = _socket.create_connection((self._config.host, self._config.port), timeout=timeout)
            self._endpoint_summary = f"{self._config.host}:{self._config.port}"
            self._transport.set_socket(sock)
            handshake_response = self._perform_handshake()
            self._protocol_version = handshake_response.get("protocol_version", self._config.protocol_version)
            if not self._is_protocol_compatible():
                raise VersionMismatchError(
                    expected=self._config.protocol_version or DEFAULT_PROTOCOL_VERSION,
                    actual=self._protocol_version,
                )
            self._authenticate_if_needed()
            self._socket = sock
            self._state = ConnectionState.CONNECTED
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "Connection established (v%s, %.1fms)",
                self._protocol_version,
                duration_ms,
            )
            return ConnectionOutcomeVO(
                state=ConnectionState.CONNECTED,
                protocol_version=self._protocol_version,
                transport_type=self._config.transport_type,
                endpoint_summary=self._endpoint_summary,
                capabilities=self._capabilities,
            )
        except VersionMismatchError:
            self._safe_close_socket(sock)
            raise
        except AuthenticationError:
            self._safe_close_socket(sock)
            raise
        except Exception as e:
            self._safe_close_socket(sock)
            self._state = ConnectionState.FAILED
            logger.error("Connection failed: %s", e)
            raise BlenderConnectionFailure(
                message=f"Connection to {self._config.host}:{self._config.port} failed: {e}",
                details={"host": self._config.host, "port": self._config.port},
            ) from e

    def disconnect(self) -> None:
        if self._state == ConnectionState.CLOSED or self._state == ConnectionState.DISCONNECTED:
            logger.debug("Already disconnected — idempotent")
            return
        try:
            if self._socket:
                self._socket.close()
        except Exception as e:
            logger.warning("Error during disconnect: %s", e)
        finally:
            self._state = ConnectionState.CLOSED
            self._socket = None
            logger.info("Connection closed")

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _safe_close_socket(self, sock: _socket.SocketType | None) -> None:
        with suppress(Exception):
            if sock is not None:
                sock.close()

    def _perform_handshake(self) -> dict:
        handshake_request = TransportMessageVO(
            tracking_id=str(uuid.uuid4()),
            operation_class="handshake",
            payload=json.dumps(
                {
                    "type": "handshake",
                    "protocol_version": self._config.protocol_version,
                }
            ).encode("utf-8"),
        )
        outcome = self._transport.send_request(handshake_request)
        if not outcome.payload:
            raise TransportParseError("Empty handshake response payload")
        response = json.loads(outcome.payload.decode("utf-8"))
        self._protocol_version = response.get("protocol_version", self._config.protocol_version)
        self._capabilities = tuple(response.get("capabilities", []))
        return response

    def _is_protocol_compatible(self) -> bool:
        return self._protocol_version.startswith("1.") or self._protocol_version.startswith("2.")

    def _authenticate_if_needed(self) -> None:
        if not self._config.auth_enabled or not self._config.auth_material:
            return
        credential_hash = hashlib.sha256(self._config.auth_material.encode("utf-8")).hexdigest()
        auth_request = TransportMessageVO(
            tracking_id=str(uuid.uuid4()),
            operation_class="authentication",
            payload=json.dumps(
                {
                    "type": "auth",
                    "credential_hash": credential_hash,
                }
            ).encode("utf-8"),
        )
        try:
            outcome = self._transport.send_request(auth_request)
            if outcome.status != "success":
                raise AuthenticationError(f"Authentication failed: {outcome.error or 'unknown error'}")
        except AuthenticationError:
            raise
        except Exception as exc:
            raise AuthenticationError(f"Authentication transport error: {exc}") from None

    def get_state(self) -> ConnectionState:
        return self._state

    def __repr__(self) -> str:
        return f"ConnectionExecutor(state={self._state.value})"
