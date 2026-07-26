"""Capability: Blender asyncio connection lifecycle management.

Implements IBlenderConnectionProtocol — handles asyncio stream connection,
handshake with version/auth, heartbeat asyncio task, reconnect with
exponential backoff, and event emission per FR-SRV-001 (v2.0.0).
No blocking I/O, no threading — pure asyncio.
"""

from __future__ import annotations

import asyncio
import json
import logging
import struct
import time

from modules.shared.src.server import (
    AuthenticationError,
    BlenderConnectionExhausted,
    BlenderConnectionFailure,
    CommandResult,
    ConnectionClosedError,
    ConnectionConfig,
    ConnectionConfigError,
    ConnectionEstablished,
    ConnectionLost,
    ConnectionState,
    DEFAULT_PROTOCOL_VERSION,
    HEARTBEAT_FAILURE_THRESHOLD,
    HEARTBEAT_INTERVAL_SECONDS,
    IBlenderConnectionProtocol,
    IEventPublisher,
    VersionMismatchError,
)

from modules.shared.src.server import (
    CONNECTION_STATE_CONNECTED,
    CONNECTION_STATE_DISCONNECTED,
    CONNECTION_STATE_FAILED,
    CONNECTION_STATE_RECONNECTING,
)

logger = logging.getLogger("BlenderMCPServer")


class BlenderConnection(IBlenderConnectionProtocol):
    """Asyncio-based persistent connection to Blender addon.

    Implements FR-SRV-001 (v2.0.0): asyncio stream connection, handshake
    with version/auth, heartbeat asyncio task, reconnect with exponential
    backoff + jitter, and event emission through IEventPublisher.

    No threading, no blocking I/O — pure asyncio throughout.
    """

    def __init__(self, event_publisher: IEventPublisher) -> None:
        """Initialize connection with event publisher.

        Args:
            event_publisher: Event bus for emitting lifecycle events.
        """
        self._event_publisher = event_publisher

        # Connection config (set on connect)
        self._config: ConnectionConfig | None = None
        self._host: str = "localhost"
        self._port: int = 9876

        # Asyncio stream
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

        # State tracking
        self._state: ConnectionState = CONNECTION_STATE_DISCONNECTED
        self._active_operation: bool = False
        self._protocol_version: str | None = DEFAULT_PROTOCOL_VERSION
        self._last_error: str | None = None
        self._reconnect_attempts: int = 0
        self._session_id: str | None = None
        self._active_file_path: str | None = None
        self._active_directory: str | None = None
        self._last_heartbeat_at: float | None = None

        # Heartbeat task
        self._heartbeat_task: asyncio.Task[None] | None = None
        self._consecutive_failures: int = 0

        # Lock for thread safety (not needed in asyncio, but kept for safety)
        self._lock: asyncio.Lock = asyncio.Lock()

    # ─── Block 2: Protocol Method Implementation ──────────────

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with handshake, auth, and version check.

        Implements FR-SRV-001 (v2.0.0): validates config, opens asyncio
        stream, performs handshake with version compatibility check,
        authenticates if required, starts heartbeat task.

        Args:
            config: Connection configuration.

        Returns:
            ConnectionStatus with state='connected'.

        Raises:
            ConnectionConfigError: Invalid config or missing auth for remote.
            VersionMismatchError: Incompatible protocol version.
            AuthenticationError: Invalid auth token.
            BlenderConnectionExhausted: All reconnect attempts failed.
        """
        self._config = config
        self._host = config.host or "localhost"
        self._port = config.port or 9876

        # Validate auth for remote connections
        if config.require_auth_for_remote and self._is_remote():
            if not config.auth_token:
                raise ConnectionConfigError(
                    message="Remote connection requires authentication token",
                    details={"host": self._host},
                )

        # Try to connect with retry/backoff
        max_attempts = config.reconnect_max_attempts if hasattr(config, 'reconnect_max_attempts') else 3
        base_delay = config.reconnect_base_delay_seconds if hasattr(config, 'reconnect_base_delay_seconds') else 1.0
        max_delay = config.reconnect_max_delay_seconds if hasattr(config, 'reconnect_max_delay_seconds') else 4.0

        for attempt in range(max_attempts):
            try:
                await self._establish_stream()
                await self._perform_handshake(config)
                await self._authenticate(config)

                # Success
                self._state = CONNECTION_STATE_CONNECTED
                self._reconnect_attempts = attempt + 1
                self._consecutive_failures = 0
                self._last_heartbeat_at = time.monotonic()

                # Start heartbeat
                self._start_heartbeat(config)

                # Emit event
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
                    attempt + 1, max_attempts, e,
                )
                await self._close_stream()

                if attempt < max_attempts - 1:
                    # Exponential backoff with jitter
                    base = min(base_delay * (2 ** attempt), max_delay)
                    jitter = (time.monotonic() % 0.5) * base
                    delay = base + jitter
                    logger.debug("Waiting %.1f seconds before reconnect attempt %d", delay, attempt + 2)
                    await asyncio.sleep(delay)

        # All retries exhausted
        self._state = CONNECTION_STATE_FAILED
        raise BlenderConnectionExhausted(
            attempts=max_attempts,
            details={"host": self._host, "port": self._port},
        )

    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent — no error if already closed.

        Stops heartbeat, closes stream, emits ConnectionLost event.
        Running operations receive ConnectionClosedError via stream close.
        """
        await self._stop_heartbeat()
        await self._close_stream()

        old_state = self._state
        self._state = CONNECTION_STATE_CLOSED

        if old_state != CONNECTION_STATE_CLOSED:
            await self._event_publisher.publish(
                ConnectionLost(reason="closed")
            )
            logger.info("Disconnected from Blender (state=%s)", CONNECTION_STATE_CLOSED)

    async def is_connected(self) -> bool:
        """Check if socket is currently connected and alive.

        Returns:
            True if connected, False otherwise.

        Raises:
            ConnectionClosedError: If connection dropped between checks.
        """
        if self._writer is None or self._writer.closed:
            raise ConnectionClosedError(details={"reason": "writer_closed"})
        return True

    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        request_id: str | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        """Send a command to Blender and return the parsed response.

        Uses asyncio stream writer with length-prefixed JSON framing.
        Parses response from stream.

        Args:
            action: The command action name.
            params: Command parameters.
            request_id: Optional tracking ID.
            timeout_ms: Optional timeout in milliseconds.

        Returns:
            CommandResult with status and data.

        Raises:
            ConnectionClosedError: If connection lost during send.
            AuthenticationError: If auth fails.
            VersionMismatchError: If version mismatch.
        """
        if self._writer is None or self._writer.closed:
            raise ConnectionClosedError(details={"reason": "no_writer"})

        try:
            # Build request payload
            payload = {
                "type": "command",
                "request_id": request_id or "",
                "action": action,
            }
            if params:
                payload["params"] = params

            # Encode and send
            json_bytes = json.dumps(payload).encode("utf-8")
            header = struct.pack("!I", len(json_bytes))
            self._writer.write(header + json_bytes)
            await self._writer.drain()

            # Receive response
            response = await self._receive_response(timeout_ms)

            # Parse response
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
            )

    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        """Receive complete JSON response from stream.

        Uses length-prefixed framing (protocol v2).

        Args:
            buffer_size: Read buffer size.

        Returns:
            Raw bytes of the JSON response.

        Raises:
            ConnectionClosedError: If connection dropped.
        """
        if self._reader is None:
            raise ConnectionClosedError(details={"reason": "no_reader"})

        # Read header (4 bytes)
        header = await self._reader.readexactly(4)
        msg_len = struct.unpack("!I", header)[0]

        # Read payload
        payload = await self._reader.readexactly(msg_len)
        return payload

    def set_active_operation_in_progress(self, active: bool) -> None:
        """Mark whether an operation is currently running.

        Used by orchestrator to coordinate heartbeat reconnection logic.
        When True, heartbeat will not trigger reconnect while operation runs.

        Args:
            active: True if an operation is in progress.
        """
        self._active_operation = active

    # ─── Block 3: Dunder Methods & Helpers ────────────────────

    def __repr__(self) -> str:
        return f"BlenderConnection(host={self._host!r}, port={self._port}, state={self._state})"

    async def _establish_stream(self) -> None:
        """Open asyncio TCP stream to Blender."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._config.connection_timeout_seconds if self._config else 30.0,
            )
        except asyncio.TimeoutError:
            raise ConnectionConfigError(
                message=f"Connection to {self._host}:{self._port} timed out",
                details={"host": self._host, "port": self._port},
            )

    async def _perform_handshake(self, config: ConnectionConfig) -> None:
        """Perform version handshake with Blender addon."""
        request_id = str(time.monotonic())

        # Send handshake request
        payload = {
            "type": "handshake",
            "request_id": request_id,
            "protocol_version": config.protocol_version or DEFAULT_PROTOCOL_VERSION,
        }
        json_bytes = json.dumps(payload).encode("utf-8")
        header = struct.pack("!I", len(json_bytes))
        self._writer.write(header + json_bytes)
        await self._writer.drain()

        # Receive handshake response
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

        # Extract protocol version and workspace info
        self._protocol_version = resp_dict.get("protocol_version", DEFAULT_PROTOCOL_VERSION)

        # Check major version compatibility
        server_major = self._parse_major(config.protocol_version or DEFAULT_PROTOCOL_VERSION)
        addon_major = self._parse_major(self._protocol_version)
        if server_major != addon_major:
            raise VersionMismatchError(
                expected=config.protocol_version or DEFAULT_PROTOCOL_VERSION,
                actual=self._protocol_version,
            )

        # Extract workspace metadata
        workspace = resp_dict.get("params", {}).get("workspace", {})
        self._session_id = resp_dict.get("result", {}).get("session_id")
        self._active_file_path = resp_dict.get("result", {}).get("active_file_path")
        self._active_directory = resp_dict.get("result", {}).get("active_directory")

    async def _authenticate(self, config: ConnectionConfig) -> None:
        """Authenticate if token is present and required."""
        if not config.auth_token:
            return  # No auth needed (local connection)

        # Send auth frame
        payload = {
            "type": "auth",
            "request_id": str(time.monotonic()),
            "token": config.auth_token,
        }
        json_bytes = json.dumps(payload).encode("utf-8")
        header = struct.pack("!I", len(json_bytes))
        self._writer.write(header + json_bytes)
        await self._writer.drain()

        # Receive auth response
        try:
            response = await self._receive_response()
            resp_dict = json.loads(response.decode("utf-8"))

            if resp_dict.get("status") == "auth_failed":
                raise AuthenticationError(
                    message="Invalid authentication token",
                    details={"host": self._host},
                )
        except ConnectionClosedError:
            raise AuthenticationError(message="Authentication connection lost")

    async def _receive_response(self, timeout_ms: float | None = None) -> bytes:
        """Receive a length-prefixed response from stream.

        Args:
            timeout_ms: Optional timeout in milliseconds.

        Returns:
            Raw bytes of the response payload.

        Raises:
            ConnectionClosedError: If connection dropped.
            asyncio.TimeoutError: If timeout exceeded.
        """
        if timeout_ms:
            timeout_s = timeout_ms / 1000.0
        else:
            timeout_s = 30.0

        # Read header (4 bytes)
        try:
            header = await asyncio.wait_for(self._reader.readexactly(4), timeout=timeout_s)
        except asyncio.TimeoutError:
            raise ConnectionClosedError(details={"reason": "response_timeout"})
        except asyncio.IncompleteReadError:
            raise ConnectionClosedError(details={"reason": "connection_dropped"})

        msg_len = struct.unpack("!I", header)[0]

        # Read payload
        try:
            payload = await asyncio.wait_for(
                self._reader.readexactly(msg_len),
                timeout=timeout_s,
            )
        except asyncio.TimeoutError:
            raise ConnectionClosedError(details={"reason": "payload_timeout"})
        except asyncio.IncompleteReadError:
            raise ConnectionClosedError(details={"reason": "connection_dropped_during_read"})

        return payload

    def _is_remote(self) -> bool:
        """Check if the configured host is remote (not localhost)."""
        return self._host not in ("localhost", "127.0.0.1", "::1")

    @staticmethod
    def _parse_major(version: str) -> int:
        """Extract major version number from semver string."""
        try:
            return int(version.split(".")[0])
        except (IndexError, ValueError):
            return 0

    # ─── Heartbeat ────────────────────────────────────────────

    def _start_heartbeat(self, config: ConnectionConfig) -> None:
        """Start the asyncio heartbeat task."""
        interval = getattr(config, 'heartbeat_interval_seconds', HEARTBEAT_INTERVAL_SECONDS) or 10
        threshold = getattr(config, 'heartbeat_failure_threshold', HEARTBEAT_FAILURE_THRESHOLD) or 3

        self._heartbeat_task = asyncio.create_task(
            self._heartbeat_loop(interval, threshold)
        )
        logger.debug("Heartbeat started (interval=%ds, threshold=%d)", interval, threshold)

    async def _stop_heartbeat(self) -> None:
        """Stop the heartbeat task."""
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def _heartbeat_loop(self, interval: int, threshold: int) -> None:
        """Heartbeat monitoring loop using asyncio sleep."""
        while True:
            try:
                await asyncio.sleep(interval)

                # Check if connection is alive (send ping)
                try:
                    request_id = str(time.monotonic())
                    payload = {
                        "type": "ping",
                        "request_id": request_id,
                    }
                    json_bytes = json.dumps(payload).encode("utf-8")
                    header = struct.pack("!I", len(json_bytes))
                    self._writer.write(header + json_bytes)
                    await self._writer.drain()

                    # Wait for pong response (short timeout — just check liveness)
                    try:
                        response = await asyncio.wait_for(
                            self._receive_response(timeout_ms=5000),
                            timeout=5.0,
                        )
                        resp_dict = json.loads(response.decode("utf-8"))
                        if resp_dict.get("status") == "ok":
                            self._consecutive_failures = 0
                            self._last_heartbeat_at = time.monotonic()
                            continue
                    except (asyncio.TimeoutError, ConnectionClosedError):
                        pass

                except ConnectionClosedError:
                    pass

                # Failure detected
                self._consecutive_failures += 1
                logger.warning(
                    "Heartbeat failure %d/%d",
                    self._consecutive_failures, threshold,
                )

                if self._consecutive_failures >= threshold:
                    # Check if operation is in progress (protect running ops)
                    if self._active_operation:
                        logger.warning(
                            "Operation in progress — deferring reconnect"
                        )
                        continue

                    # Trigger reconnect
                    self._state = CONNECTION_STATE_RECONNECTING
                    await self._event_publisher.publish(
                        ConnectionLost(reason="heartbeat_timeout")
                    )
                    await self._close_stream()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Heartbeat error: %s", e)
                self._consecutive_failures += 1

    async def _close_stream(self) -> None:
        """Close the asyncio stream cleanly."""
        if self._writer is not None and not self._writer.closed:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = None
        self._writer = None
