"""Gateway domain contract: connection maintenance protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-GWY-002: Maintain Connection via heartbeat, liveness detection, and reconnect.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import ConnectionState, ConnectionStatusVO


class ConnectionMaintenanceProtocol(ABC):
    """Protocol interface for heartbeat, liveness detection, and reconnection."""

    @abstractmethod
    def get_connection_status(self) -> ConnectionStatusVO:
        """Query current connection state including liveness signals.

        FR-GWY-002: Returns continuously updated state with last heartbeat,
        reconnect attempts, and failure reason.
        """
        ...

    @abstractmethod
    def send_heartbeat(self) -> None:
        """Send heartbeat to verify liveness.

        FR-GWY-002: Independent from main-thread execution where supported.
        Does not trigger reconnect during active long-running operations.
        """
        ...

    @abstractmethod
    def attempt_reconnect(self) -> ConnectionStatusVO:
        """Attempt reconnection with retry policy and backoff.

        FR-GWY-002: Increasing backoff with jitter. Transitions to failed state
        when retry exhaustion occurs. Emits observability events.
        """
        ...

    @abstractmethod
    def set_state(self, state: ConnectionState | None) -> None:
        """Set the current connection state.

        FR-GWY-002: Allows the orchestrator to update state through the
        protocol interface rather than reaching into concrete implementations.
        Pass None to transition to closed/disconnected state.
        """
        ...
