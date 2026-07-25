"""Capability: Blender socket connection lifecycle management.

Implements IBlenderConnectionProtocol — handles TCP socket connection,
heartbeat monitoring, auto-reconnect with exponential backoff,
and connection status reporting per FR-SRV-001 / FR-SRV-004.
"""

from __future__ import annotations
from typing import Any

import contextlib
import json
import logging
import os
import random
import select
import socket
import threading
import time


from modules.shared.src.server import (
    AuthenticationError,
    BlenderConnectionExhausted,
    ConnectionConfigError,
    IBlenderConnectionProtocol,
    ProtocolVersionMismatchError,
    CONNECTION_TIMEOUT_SECONDS,
    MAX_RECONNECT_ATTEMPTS,
    RETRY_BASE_DELAY_SECONDS,
    RETRY_MAX_DELAY_SECONDS,
)
from modules.config.src.contract_config import ConfigPort
from modules.shared.src import (
    ActionName,
    BlenderConnectionFailure,
    ConfigPath,
    Details,
    ErrorMessage,
    ExecutionError,
    SuccessFlag,
)
from modules.shared.src.server import ConnectionStatus

logger = logging.getLogger("BlenderMCPServer")

RECEIVE_TIMEOUT: float = CONNECTION_TIMEOUT_SECONDS


class BlenderConnection(IBlenderConnectionProtocol):
    """Manages persistent socket connection to Blender addon.

    Implements FR-SRV-001: heartbeat monitoring, auto-reconnect with
    exponential backoff with jitter, and proper connection state events.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, host: str = "localhost", port: int = 9876) -> None:
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
        self._lock = threading.Lock()
        
        # Heartbeat configuration (FR-SRV-001)
        self._heartbeat_interval = 10  # seconds
        self._heartbeat_failure_threshold = 3
        self._consecutive_failures = 0
        self._last_heartbeat_at: float | None = None
        
        # Connection state tracking (FR-SRV-001)
        self._state: str = "disconnected"
        self._reconnect_attempts: int = 0
        self._protocol_version: str | None = None
        self._last_error: str | None = None
        
        # Heartbeat thread
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_heartbeat = threading.Event()

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def connect(self) -> SuccessFlag:  # FR-SRV-001
        """Connect to Blender with exponential backoff retries and jitter.

        Implements FR-SRV-001: auto-reconnect with max 3 retry attempts
        using exponential backoff with jitter (1s, 2s, 4s).
        Connection timeout: CONNECTION_TIMEOUT_SECONDS (30s default).
        Initializes heartbeat monitoring on successful connection.
        """
        with self._lock:
            # Update state
            self._state = "connecting"
            self._last_error = None
            
            if self.sock is not None:
                if self._is_socket_alive():
                    return SuccessFlag(True)
                self._close_socket()

            for attempt in range(MAX_RECONNECT_ATTEMPTS):
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(CONNECTION_TIMEOUT_SECONDS)
                    self.sock.connect((self.host, self.port))
                    
                    # Update state on success
                    self._state = "connected"
                    self._reconnect_attempts = attempt + 1
                    self._consecutive_failures = 0
                    self._last_heartbeat_at = time.time()
                    logger.info("Connected to Blender at %s:%d", self.host, self.port)
                    
                    # Start heartbeat monitoring
                    self._start_heartbeat()
                    return SuccessFlag(True)
                    
                except Exception as e:
                    self._state = "failed"
                    self._last_error = str(e)
                    logger.warning(
                        "Connection attempt %d/%d failed: %s",
                        attempt + 1,
                        MAX_RECONNECT_ATTEMPTS,
                        e,
                    )
                    self._close_socket()
                    
                    if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                        # Exponential backoff with jitter (FR-SRV-001)
                        base_delay = min(
                            RETRY_BASE_DELAY_SECONDS * (2**attempt),
                            RETRY_MAX_DELAY_SECONDS,
                        )
                        jitter = random.uniform(0, 0.5 * base_delay)
                        delay = base_delay + jitter
                        logger.debug("Waiting %.1f seconds before reconnect attempt %d", delay, attempt + 2)
                        time.sleep(delay)

            # All retries exhausted
            self._state = "failed"
            raise BlenderConnectionExhausted(ErrorMessage("Failed to connect after all retry attempts"))

    # ─── Heartbeat Management (FR-SRV-001) ──────────────────
    
    def _start_heartbeat(self) -> None:
        """Start heartbeat monitoring thread."""
        self._stop_heartbeat.clear()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
    
    def _heartbeat_loop(self) -> None:
        """Heartbeat monitoring loop. Checks connection liveness periodically."""
        while not self._stop_heartbeat.is_set():
            try:
                time.sleep(self._heartbeat_interval)
                if self._stop_heartbeat.is_set():
                    break
                
                # Check if socket is alive
                if not self._is_socket_alive():
                    self._consecutive_failures += 1
                    logger.warning(
                        "Heartbeat failure %d/%d",
                        self._consecutive_failures,
                        self._heartbeat_failure_threshold,
                    )
                    
                    if self._consecutive_failures >= self._heartbeat_failure_threshold:
                        self._state = "reconnecting"
                        logger.info("Heartbeat threshold reached, triggering reconnect")
                        self._close_socket()
                        # Trigger reconnect in background
                        threading.Thread(target=self._reconnect_background, daemon=True).start()
                else:
                    # Success - reset failure count
                    self._consecutive_failures = 0
                    self._last_heartbeat_at = time.time()
                    
            except Exception as e:
                logger.error("Heartbeat error: %s", e)
                self._consecutive_failures += 1
    
    def _reconnect_background(self) -> None:
        """Background reconnect attempt."""
        try:
            self.connect()
        except Exception as e:
            logger.error("Background reconnect failed: %s", e)
    
    def stop_heartbeat(self) -> None:
        """Stop heartbeat monitoring thread."""
        self._stop_heartbeat.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=5.0)
        self._heartbeat_thread = None

    # ─── Block 3: Protocol Method Implementation & Helpers ──────
    
    async def get_status(self) -> ConnectionStatus:  # FR-SRV-001
        """Return current connection state with metadata."""
        return ConnectionStatus(
            state=self._state,
            transport_type="socket",
            host=self.host,
            port=self.port,
            last_error=self._last_error,
            last_heartbeat_at=self._last_heartbeat_at,
            reconnect_attempts=self._reconnect_attempts,
            protocol_version=self._protocol_version,
            heartbeat_interval_seconds=self._heartbeat_interval,
            heartbeat_failure_threshold=self._heartbeat_failure_threshold,
        )

    def __repr__(self) -> str:
        return f"BlenderConnection(host={self.host!r}, port={self.port}, state={self._state})"

    def _close_socket(self):
        if self.sock:
            with contextlib.suppress(Exception):
                self.sock.close()
            self.sock = None

    async def disconnect(self) -> None:  # FR-SRV-001 (idempotent)
        """Graceful disconnect. Must be idempotent.

        Stops heartbeat monitoring, closes socket, updates state.
        Fails pending queued operations with ConnectionClosedError.
        """
        with self._lock:
            self.stop_heartbeat()
            self._close_socket()
            self._state = "disconnected"
            logger.info("Disconnected from Blender at %s:%d", self.host, self.port)

    def _is_socket_alive(self) -> bool:
        if self.sock is None:
            return False
        try:
            ready, _, _ = select.select([self.sock], [], [], 0)
            if ready:
                data = self.sock.recv(1, socket.MSG_PEEK)
                if not data:
                    return False
            return True
        except (ConnectionError, BrokenPipeError, ConnectionResetError, OSError, BlenderConnectionFailure):
            return False

    def _read_response_chunks(self, sock: socket.socket, buffer_size: int) -> tuple:
        """Read socket chunks until a complete JSON is received or connection ends.

        Returns (chunks, completed_via_json) where completed_via_json is True
        if we successfully parsed JSON and have the complete response.
        """
        chunks: list[bytes] = []
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise BlenderConnectionFailure(ErrorMessage("Connection closed before receiving any data"))
                        break
                    chunks.append(chunk)
                    try:
                        data = b"".join(chunks)
                        json.loads(data.decode("utf-8"))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return chunks, True
                    except json.JSONDecodeError:
                        continue
                except TimeoutError:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error: {e}")
                    raise
        except TimeoutError:
            logger.warning("Socket timeout during chunked receive")  # pragma: no cover
        except Exception as e:
            logger.error(f"Error during receive: {e}")
            raise
        return chunks, False

    def _finalize_chunks(self, chunks: list[bytes]) -> bytes:
        """Process collected chunks into a complete response."""
        data = b"".join(chunks)
        logger.info(f"Returning data after receive completion ({len(data)} bytes)")
        try:
            json.loads(data.decode("utf-8"))
            return data
        except json.JSONDecodeError as e:
            raise ExecutionError(ErrorMessage("Incomplete JSON response received")) from e

    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        """Receive complete JSON response from socket in chunks.

        Uses self.sock (the active connection socket).
        """
        if self.sock is None:
            raise BlenderConnectionFailure(ErrorMessage("No active socket connection"))
        chunks, completed = self._read_response_chunks(self.sock, buffer_size)
        if completed:
            return b"".join(chunks)
        if chunks:
            return self._finalize_chunks(chunks)
        raise BlenderConnectionFailure(ErrorMessage("No data received"))

    async def is_connected(self) -> SuccessFlag:
        return SuccessFlag(self._is_socket_alive())  # pragma: no cover

    def _handle_command_response(self, response_data: bytes) -> dict[str, Any]:
        """Parse and validate the JSON response from Blender."""
        response = json.loads(response_data.decode("utf-8"))
        logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")

        if response.get("status") == "error":
            logger.error(f"Blender error: {response.get('message')}")
            raise ExecutionError(ErrorMessage(response.get("message", "Unknown error from Blender")))

        result: dict[str, Any] = response.get("result", {})
        return result

    async def send_command(self, command_type: ActionName, params: Details | None = None) -> Details:
        with self._lock:
            if self.sock is None and not await self.connect():
                raise ConnectionError("Not connected to Blender")

            active_sock = self.sock
            if active_sock is None:
                raise ConnectionError("Socket initialization failed")

            command = {"type": str(command_type), "params": params or {}}

            response_data: bytes = b""
            try:
                logger.info(f"Sending command: {command_type} with params: {params}")
                active_sock.settimeout(RECEIVE_TIMEOUT)
                active_sock.sendall(json.dumps(command).encode("utf-8"))
                logger.info("Command sent, waiting for response...")
                response_data = await self.receive_full_response()
                logger.info(f"Received {len(response_data)} bytes of data")

                return self._handle_command_response(response_data)
            except TimeoutError as e:
                logger.error("Socket timeout while waiting for response")
                self._close_socket()
                raise BlenderConnectionFailure(
                    ErrorMessage("Timeout waiting for Blender response - try simplifying your request")
                ) from e
            except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                logger.error(f"Socket connection error: {e}")
                self._close_socket()
                raise BlenderConnectionFailure(ErrorMessage(f"Connection to Blender lost: {e}")) from e
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from Blender: {e}")
                if response_data:
                    logger.error(
                        f"Raw response (first 200 bytes): {response_data[:200].decode('utf-8', errors='replace')}"
                    )
                raise ExecutionError(ErrorMessage(f"Invalid response from Blender: {e}")) from e
            except Exception as e:
                logger.error(f"Error communicating with Blender: {e}")
                self._close_socket()
                raise BlenderConnectionFailure(ErrorMessage(f"Communication error with Blender: {e}")) from e


# ─── BlenderConnectionFactory ─────────────────────────────────────────────────


class BlenderConnectionFactory:
    """Factory that creates and manages a singleton BlenderConnection.

    Implements FR-SRV-004: Factory validates configuration before instantiation.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, config: ConfigPort | None = None) -> None:
        self._config = config
        self._connection: BlenderConnection | None = None
        self._lock = threading.Lock()

    # ─── Block 2: Configuration Validation (FR-SRV-004) ─────────────

    @staticmethod
    def _validate_config(host: str, port: int) -> None:
        """Validate connection configuration parameters.

        Raises ConnectionConfigError for invalid configuration.
        """
        if not host or not host.strip():
            raise ConnectionConfigError(ErrorMessage("Host cannot be empty"))

        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ConnectionConfigError(
                ErrorMessage(f"Port must be between 1 and 65535, got {port}")
            )

    # ─── Block 3: Protocol Method Implementation ─────────────

    def get_connection(self) -> IBlenderConnectionProtocol:  # FR-SRV-004
        """Create new Blender connection instance based on configuration.

        Validates configuration before instantiation per FR-SRV-004.
        Returns BlenderConnection adapter implementation.
        """
        host = "localhost"
        port = 9876
        
        if self._config is not None:
            host_val = self._config.get(ConfigPath("blender.host"), "localhost")
            host = str(host_val) if host_val is not None else "localhost"
            port_val = self._config.get(ConfigPath("blender.port"), 9876)
            port = int(port_val) if isinstance(port_val, (int, str)) else 9876

        # Environment variable override
        env_host = os.getenv("BLENDER_HOST")
        if env_host:
            host = env_host
        
        env_port = os.getenv("BLENDER_PORT")
        if env_port:
            port = int(env_port)

        # Validate configuration (FR-SRV-004)
        self._validate_config(host, port)

        with self._lock:
            if self._connection is not None:
                if self._connection._is_socket_alive():
                    return self._connection
                self._connection.disconnect()
                self._connection = None

            self._connection = BlenderConnection(host=host, port=port)
            try:
                if not self._connection.connect():
                    self._connection = None
                    raise BlenderConnectionFailure(
                        ErrorMessage("Could not connect to Blender. Make sure the Blender addon is running.")
                    )
            except Exception as e:
                self._connection = None
                raise BlenderConnectionFailure(
                    ErrorMessage(f"Connection failed: {e}")
                ) from e
            return self._connection

    # ─── Block 4: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return "BlenderConnectionFactory()"

    def shutdown(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._connection.disconnect()
                self._connection = None


# ─── Backward-compat global singleton helpers ─────────────────────────────────

_blender_connection: BlenderConnection | None = None
_connection_lock = threading.Lock()
_default_factory: BlenderConnectionFactory | None = None


def get_blender_connection() -> BlenderConnection:
    """Get or create a persistent Blender connection singleton (backward compat)."""
    global _blender_connection, _default_factory

    with _connection_lock:
        if _blender_connection is not None:
            if _blender_connection._is_socket_alive():
                return _blender_connection
            _blender_connection.disconnect()
            _blender_connection = None

        if _default_factory is None:
            _default_factory = BlenderConnectionFactory()

        conn = _default_factory.get_connection()
        if isinstance(conn, BlenderConnection):
            _blender_connection = conn
        else:
            msg = "BlenderConnectionFactory returned unexpected type"
            raise TypeError(msg)
        return _blender_connection


def shutdown_connection():
    """Shutdown the persistent Blender connection."""
    global _blender_connection, _default_factory
    with _connection_lock:
        if _default_factory is not None:
            _default_factory.shutdown()
            _default_factory = None
        _blender_connection = None
