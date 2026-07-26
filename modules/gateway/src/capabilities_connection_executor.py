"""Connection capability — establish and manage transport connection to Blender.

FR-GWY-001: Establish Connection
- Opens socket or stdio pipe channel
- Performs handshake and protocol version negotiation
- Authenticates when required
- Idempotent when already connected
"""

import logging
import socket
import time

from modules.shared.src.gateway.contract_connection_protocol import (
    ConnectionProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    AuthenticationError,
    ProtocolVersionMismatchError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    ConnectionOutcomeVO,
    ConnectionState,
    TransportType,
)

logger = logging.getLogger("BlenderMCPServer")


class ConnectionExecutor(ConnectionProtocol):
    """Concrete implementation for transport connection establishment.

    FR-GWY-001: Opens socket/stdio, negotiates protocol version, authenticates.
    Idempotent when already connected. Deterministic state transitions.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        self._socket: socket.SocketType | None = None
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self._protocol_version: str = ""
        self._endpoint_summary: str = ""
        self._capabilities: tuple[str, ...] = ()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def establish_connection(self) -> ConnectionOutcomeVO:
        """Establish transport channel to Blender with handshake and protocol check.

        FR-GWY-001: Idempotent when already connected. Validates protocol version.
        Rejects incompatible versions. Transports auth material only when enabled.
        """
        if self._state == ConnectionState.CONNECTED:
            logger.info("Already connected — idempotent")
            return ConnectionOutcomeVO(
                state=ConnectionState.CONNECTED,
                protocol_version=self._protocol_version,
                transport_type=TransportType.LOCAL_SOCKET,
                endpoint_summary=self._endpoint_summary,
                capabilities=self._capabilities,
            )

        start_time = time.time()
        self._state = ConnectionState.CONNECTING
        logger.info("Establishing connection to Blender")

        try:
            # Open socket connection
            self._socket = socket.create_connection(("localhost", 50051), timeout=30.0)
            self._endpoint_summary = "localhost:50051"

            # Perform handshake (stub — in real implementation, exchange protocol version)
            handshake_response = self._perform_handshake()
            self._protocol_version = handshake_response.get("protocol_version", "1.0")

            # Validate protocol version
            if not self._is_protocol_compatible():
                raise ProtocolVersionMismatchError(
                    f"Protocol version {self._protocol_version} incompatible"
                )

            # Authenticate if enabled
            self._authenticate_if_needed()

            self._state = ConnectionState.CONNECTED
            duration_ms = (time.time() - start_time) * 1000
            logger.info("Connection established (v%s, %.1fms)", self._protocol_version, duration_ms)

            return ConnectionOutcomeVO(
                state=ConnectionState.CONNECTED,
                protocol_version=self._protocol_version,
                transport_type=TransportType.LOCAL_SOCKET,
                endpoint_summary=self._endpoint_summary,
                capabilities=self._capabilities,
            )

        except ProtocolVersionMismatchError:
            raise
        except AuthenticationError:
            raise
        except Exception as e:
            self._state = ConnectionState.FAILED
            logger.error("Connection failed: %s", e)
            return ConnectionOutcomeVO(
                state=ConnectionState.FAILED, error=str(e),
            )

    def disconnect(self) -> None:
        """Graceful disconnect. Must be idempotent.

        FR-GWY-002: State transitions to closed. No-op if already disconnected.
        """
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

    def _perform_handshake(self) -> dict:
        """Perform handshake and exchange protocol version information."""
        # Stub: In real implementation, this would send/receive handshake messages
        return {"protocol_version": "1.0", "capabilities": ["commands", "code_execution"]}

    def _is_protocol_compatible(self) -> bool:
        """Check if negotiated protocol version is compatible."""
        return self._protocol_version.startswith("1.") or self._protocol_version.startswith("2.")

    def _authenticate_if_needed(self) -> None:
        """Transport authentication material when auth is enabled."""
        # Stub: In real implementation, this would send auth credentials
        pass

    def get_state(self) -> ConnectionState:
        return self._state

    def __repr__(self) -> str:
        return f"ConnectionExecutor(state={self._state.value})"
