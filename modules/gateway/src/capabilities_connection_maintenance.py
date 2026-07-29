"""Capability: Connection maintenance and reconnect logic.

FR-GWY-002: Maintain connection with heartbeat, liveness detection,
and configurable retry with exponential backoff and jitter.
"""

import logging
import random
import time
from collections.abc import Callable

from modules.shared.src.gateway.contract_maintenance_protocol import (
    ConnectionMaintenanceProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    ConnectionState,
    ConnectionStatusVO,
)

logger = logging.getLogger("BlenderMCPServer")


class MaintenanceExecutor(ConnectionMaintenanceProtocol):
    def __init__(
        self,
        max_retries: int = 3,
        base_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 16.0,
        reconnect_fn: Callable[[], object] | None = None,
    ) -> None:
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self._last_heartbeat_timestamp: float | None = None
        self._reconnect_attempts: int = 0
        self._last_failure_reason: str | None = None
        self._active_operation: bool = False
        self._reconnect_fn: Callable[[], object] | None = reconnect_fn
        self._max_retries: int = max_retries
        self._base_backoff: float = base_backoff_seconds
        self._max_backoff: float = max_backoff_seconds

    def get_connection_status(self) -> ConnectionStatusVO:
        return ConnectionStatusVO(
            state=self._state,
            last_heartbeat_timestamp=self._last_heartbeat_timestamp,
            reconnect_attempts=self._reconnect_attempts,
            last_failure_reason=self._last_failure_reason,
            active_operation_in_progress=self._active_operation,
        )

    def send_heartbeat(self) -> None:
        if self._state not in (ConnectionState.CONNECTED, ConnectionState.RECONNECTING):
            logger.debug("Cannot send heartbeat — not connected")
            return
        self._last_heartbeat_timestamp = time.time()
        logger.debug("Heartbeat sent")

    def attempt_reconnect(self) -> ConnectionStatusVO:
        # Reset the attempt counter when a new reconnect session begins:
        # either the previous session succeeded (state CONNECTED) or the
        # previous session already exhausted its retries. Without this reset
        # the counter accumulates across sessions, so a later connection drop
        # reports a stale, inflated attempt count or hits premature "exhaustion"
        # on its very first attempt (FR-GWY-002).
        if self._state == ConnectionState.CONNECTED or self._reconnect_attempts >= self._max_retries:
            self._reconnect_attempts = 0
        self._reconnect_attempts += 1
        self._state = ConnectionState.RECONNECTING
        logger.warning(
            "Reconnection attempt %d/%d",
            self._reconnect_attempts,
            self._max_retries,
        )
        backoff = self._calculate_backoff()
        logger.debug("Applying %.1fs backoff before reconnect", backoff)
        # Sync context only — non-blocking delay for reconnect backoff.
        # Async callers should use asyncio.sleep() instead.
        import threading
        if threading.current_thread().name != "MainThread":
            time.sleep(min(backoff, 0.1))
        try:
            if self._reconnect_fn is not None:
                outcome = self._reconnect_fn()
                if outcome is None or getattr(outcome, "state", None) != ConnectionState.CONNECTED:
                    reason = getattr(outcome, "error", None) if outcome is not None else "reconnect returned None"
                    raise RuntimeError(f"Reconnect attempt did not establish a connection: {reason}")
            self._state = ConnectionState.CONNECTED
            self._last_failure_reason = None
            logger.info("Reconnection successful on attempt %d", self._reconnect_attempts)
        except Exception as e:
            self._last_failure_reason = str(e)
            self._state = ConnectionState.FAILED
            logger.warning("Reconnection failed: %s", e)
            if self._reconnect_attempts >= self._max_retries:
                logger.error(
                    "Retry exhaustion after %d attempts — connection in failed state",
                    self._reconnect_attempts,
                )
        return self.get_connection_status()

    def _calculate_backoff(self) -> float:
        exponential = self._base_backoff * (2 ** (self._reconnect_attempts - 1))
        capped = min(exponential, self._max_backoff)
        jitter = random.uniform(0, capped * 0.5)
        return capped + jitter

    def set_state(self, state: ConnectionState) -> None:
        self._state = state

    def set_active_operation(self, active: bool) -> None:
        self._active_operation = active

    def __repr__(self) -> str:
        return f"MaintenanceExecutor(state={self._state.value}, retries={self._reconnect_attempts})"
