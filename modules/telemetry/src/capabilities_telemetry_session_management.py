"""Capability: Telemetry session manager.

FR-TLM-003: Manages anonymous session identifiers with persistence,
rotation, and consent withdrawal support.

Implements TelemetrySessionProtocol — async protocol with file-based
persistence and consent-aware session retrieval.
"""

from __future__ import annotations

import json
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

logger = logging.getLogger("blender-arwaky.telemetry")

# Default persistence path (overridable for testing)
_DEFAULT_SESSION_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "session.json",
)


class TelemetrySessionManager(TelemetrySessionProtocol):
    """Telemetry session management with persistence and rotation.

    FR-TLM-003: Session ID survives restarts within rotation window.
    Rotation produces fresh ID with no stored linkage.
    Consent withdrawal deletes all local session state.
    """

    def __init__(self, persistence_path: str | None = None) -> None:
        self._session_id: SessionId | None = None
        self._creation_timestamp: float | None = None
        self._persistence_path = persistence_path or _DEFAULT_SESSION_PATH
        self._lock = threading.Lock()

    async def get_session_id(
        self,
        force_new: bool = False,
        consent_active: bool = True,
    ) -> SessionId:
        """Get current session ID. Returns None if consent inactive.

        FR-TLM-003: If consent is inactive, raises RuntimeError.
        """
        if not consent_active:
            raise RuntimeError("Telemetry consent is inactive")

        with self._lock:
            if self._session_id is not None and not force_new:
                return self._session_id

            # Load from persistence or generate new
            self._session_id = self._load_or_generate_session()
            self._creation_timestamp = self._current_timestamp()
            return self._session_id

    async def rotate_session(self) -> SessionId:
        """Rotate session, producing fresh identifier with no linkage.

        FR-TLM-003: Rotation discards old ID; buffered records may still
        transmit, but no future refs will be linked to old session.
        """
        with self._lock:
            # Save current session for potential audit (not stored long-term)
            if self._session_id is not None:
                logger.debug("Session %s rotated at %f", self._session_id, self._creation_timestamp)

            self._session_id = SessionId(str(uuid.uuid4()))
            self._creation_timestamp = self._current_timestamp()
            self._persist_session()
            logger.debug("Session rotated: %s", self._session_id)
            return self._session_id

    async def clear_session(self) -> None:
        """Clear session state — called on consent withdrawal.

        FR-TLM-003: Deletes local session state entirely.
        """
        with self._lock:
            self._session_id = None
            self._creation_timestamp = None
            self._delete_persistence()
            logger.debug("Session cleared (consent withdrawal)")

    def get_session_id_sync(self) -> SessionId | None:
        """Sync access to current session ID (for non-async callers)."""
        with self._lock:
            return self._session_id

    def initialize_session(self) -> SuccessFlag:
        """Generate a new anonymous session identifier.

        Called on application startup.
        """
        with self._lock:
            self._session_id = SessionId(str(uuid.uuid4()))
            self._creation_timestamp = self._current_timestamp()
            self._persist_session()
            return SuccessFlag(True)

    def _load_or_generate_session(self) -> SessionId:
        """Load persisted session or generate new one."""
        try:
            data = self._load_persistence()
            if data and data.get("session_id"):
                logger.debug("Loaded persisted session: %s", data["session_id"])
                return SessionId(data["session_id"])
        except Exception as e:
            logger.warning("Failed to load session persistence: %s", e)

        # Generate fresh session
        return SessionId(str(uuid.uuid4()))

    def _persist_session(self) -> None:
        """Save session state to disk."""
        try:
            data = {
                "session_id": str(self._session_id),
                "created_at": self._creation_timestamp,
            }
            with open(self._persistence_path, "w") as f:
                json.dump(data, f)
        except OSError as e:
            logger.warning("Failed to persist session: %s", e)

    def _load_persistence(self) -> dict | None:
        """Load session state from disk."""
        try:
            with open(self._persistence_path, "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def _delete_persistence(self) -> None:
        """Delete session persistence file."""
        try:
            if os.path.exists(self._persistence_path):
                os.remove(self._persistence_path)
        except OSError as e:
            logger.warning("Failed to delete session persistence: %s", e)

    def _current_timestamp(self) -> float:
        """Return current Unix timestamp."""
        import time

        return time.time()
