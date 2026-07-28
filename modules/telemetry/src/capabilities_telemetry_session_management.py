"""Capability: Telemetry session manager.

Implements TelemetrySessionManagementPort — handles anonymous session identifier
generation and management per FR-TLM-003.
"""

from __future__ import annotations

import logging
import os
import threading
import uuid

from modules.shared.src.common.taxonomy_core_vo import (
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)

logger = logging.getLogger("blender-arwaky-telemetry-service")


class TelemetrySessionManager(TelemetrySessionProtocol):
    """Telemetry session management implementation.

    FR-TLM-003: Manages anonymous session identifiers that persist
    for the entire application runtime. New IDs generated on restart.
    """

    def __init__(self) -> None:
        self._session_id: SessionId | None = None
        self._lock = threading.Lock()

    def get_session_id(self) -> SessionId:
        """Return the current anonymous session identifier.

        FR-TLM-003: The session ID persists for the entire application runtime.
        If no session exists, generates a new one automatically.
        """
        if self._session_id is None:
            with self._lock:
                # Double-check after acquiring lock
                if self._session_id is None:
                    self._session_id = self._generate_session_id()

        return self._session_id

    def initialize_session(self) -> SuccessFlag:
        """Generate a new anonymous session identifier.

        FR-TLM-003: Called on application startup to create a fresh session.
        The identifier must be completely anonymous and not traceable to a user.
        """
        with self._lock:
            self._session_id = self._generate_session_id()
            return SuccessFlag(True)

    def _generate_session_id(self) -> SessionId:
        """Generate a completely anonymous session identifier.

        Uses uuid4 for cryptographically random, anonymous identifiers.
        Falls back to simple random string if uuid4 fails.
        """
        try:
            # Primary method: UUID4 (cryptographically random)
            return SessionId(str(uuid.uuid4()))
        except Exception as e:
            logger.debug("UUID4 generation failed, using fallback: %s", e)
            # Fallback: simple random string
            try:
                random_id = uuid.uuid4().hex
                return SessionId(f"session-{random_id}")
            except Exception as fallback_error:
                logger.error("Session ID generation failed completely: %s", fallback_error)
                # Ultimate fallback: use process ID (still anonymous)
                return SessionId(f"session-proc-{os.getpid()}")
