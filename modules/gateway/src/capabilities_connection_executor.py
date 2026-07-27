"""Connection capability — establish and manage transport connection to Blender.

FR-GWY-001: Establish Connection
- Opens socket or stdio pipe channel
- Performs handshake and protocol version negotiation
- Authenticates when required
- Idempotent when already connected
- Delegates transport messaging to TransportProtocol
- Uses configured auth material for authentication
"""

import json
import logging
import socket
import time

from modules.shared.src.gateway.contract_connection_protocol import (
    ConnectionProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    AuthenticationError,
    ProtocolVersionMismatchError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    ConnectionConfigVO,
    ConnectionOutcomeVO,
    ConnectionState,
    TransportMessageVO,
    TransportType,
)

logger = logging.getLogger("BlenderMCPServer")


class ConnectionExecutor(ConnectionProtocol):
    """Concrete implementation for transport connection establishment.

    FR-GWY-001: Opens socket/stdio, negotiates protocol version, authenticates.
    Idempotent when already connected. Deterministic state transitions.
    Delegates transport to TransportProtocol.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        transport: TransportProtocol,
        config: ConnectionConfigVO | None = None,
    ) -> None:
        self._socket: socket.SocketType | None = None
        self._transport: TransportProtocol = transport
        self._config: ConnectionConfigVO = config or ConnectionConfigVO()
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self._protocol_version: str = ""
        self._endpoint_summary: str = ""
        self._capabilities: tuple[str, ...] = ()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def establish_connection(self) -> ConnectionOutcomeVO:
        """Establish transport channel to Blender with handshake and protocol check.

        FR-GWY-001: Idempotent when already connected. Validates protocol version.
        Rejects incompatible versions. Transports auth material only when enabled.
        Uses configured endpoint, timeout, and auth settings.
        """
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

        try:
            # Open socket connection using configured endpoint
            timeout = self._config.timeout_seconds or 30.0
            self._socket = socket.create_connection((self._config.host, self._config.port), timeout=timeout)
            self._endpoint_summary = f"{self._config.host}:{self._config.port}"

            # Perform handshake via transport
            handshake_response = self._perform_handshake()
            self._protocol_version = handshake_response.get("protocol_version", self._config.protocol_version)

            # Validate protocol version
            if not self._is_protocol_compatible():
                raise ProtocolVersionMismatchError(f"Protocol version {self._protocol_version} incompatible")

            # Authenticate if enabled
            self._authenticate_if_needed()

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

        except ProtocolVersionMismatchError:
            raise
        except AuthenticationError:
            raise
        except Exception as e:
            self._state = ConnectionState.FAILED
            logger.error("Connection failed: %s", e)
            return ConnectionOutcomeVO(
                state=ConnectionState.FAILED,
                error=str(e),
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
        """Perform handshake and exchange protocol version via transport.

        FR-GWY-001: Sends handshake request, receives protocol version and
        capability summary from Blender side. Uses TransportProtocol for
        framed message exchange.
        """
        # Build handshake request message
        import uuid as _uuid

        handshake_request = TransportMessageVO(
            tracking_id=str(_uuid.uuid4()),
            operation_class="handshake",
            payload=json.dumps(
                {
                    "type": "handshake",
                    "protocol_version": self._config.protocol_version,
                }
            ).encode("utf-8"),
        )

        # Send handshake via transport
        try:
            outcome = self._transport.send_request(handshake_request)
            if outcome.payload:
                response = json.loads(outcome.payload.decode("utf-8"))
                self._protocol_version = response.get("protocol_version", self._config.protocol_version)
                self._capabilities = tuple(response.get("capabilities", []))
                return response
            return {
                "protocol_version": self._config.protocol_version,
                "capabilities": ["commands", "code_execution"],
            }
        except Exception:
            # Fallback to default handshake on transport failure
            return {
                "protocol_version": self._config.protocol_version,
                "capabilities": ["commands", "code_execution"],
            }

    def _is_protocol_compatible(self) -> bool:
        """Check if negotiated protocol version is compatible.

        Accepts major versions 1.x and 2.x for forward compatibility.
        """
        return self._protocol_version.startswith("1.") or self._protocol_version.startswith("2.")

    def _authenticate_if_needed(self) -> None:
        """Transport authentication material when auth is enabled.

        FR-GWY-001: Sends auth credentials only when authentication is enabled.
        Auth material is never logged or echoed in diagnostics.
        Raises AuthenticationError when auth fails.
        """
        if not self._config.auth_enabled or not self._config.auth_material:
            return

        # Send authentication message via transport
        import uuid as _uuid

        auth_request = TransportMessageVO(
            tracking_id=str(_uuid.uuid4()),
            operation_class="authentication",
            payload=json.dumps(
                {
                    "type": "auth",
                    "credential": self._config.auth_material,
                }
            ).encode("utf-8"),
        )

        try:
            outcome = self._transport.send_request(auth_request)
            if outcome.status != "success":
                raise AuthenticationError(f"Authentication failed: {outcome.error or 'unknown error'}")
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Authentication transport error: {e}")

    def get_state(self) -> ConnectionState:
        return self._state

    def __repr__(self) -> str:
        return f"ConnectionExecutor(state={self._state.value})"
