"""Capability: Telemetry session manager.

Implements TelemetrySessionProtocol — maintains random, unlinkable
session identifiers that survive restarts within a rotation window.

FR-TLM-003: Manage Analytics Sessions
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any
from uuid import uuid4

from modules.shared.src.telemetry.contract_telemetry_session_protocol import TelemetrySessionProtocol
from modules.shared.src.common.taxonomy_core_vo import SessionId, Timestamp

logger = logging.getLogger("BlenderMCPServer")


class TelemetrySessionCapability(TelemetrySessionProtocol):
    """Business logic for managing anonymous telemetry sessions."""

    def __init__(
        self,
        session_file: str | None = None,
        rotation_interval_hours: float = 24.0,
    ) -> None:
        """Initialize with optional session persistence file.

        Args:
            session_file: Path to persist session state. None = in-memory only.
            rotation_interval_hours: Session lifetime before forced rotation.
        """
        self._session_file = session_file
        self._rotation_interval_seconds = rotation_interval_hours * 3600
        self._current_session_id: str | None = None
        self._created_timestamp: float | None = None
        self._load_session()

    async def get_session_id(
        self,
        force_new: bool = False,
        consent_active: bool = True,
    ) -> str:
        """Get current session ID or generate fresh one.

        FR-TLM-003: Session ID generated from collision-resistant random source.
        Persists across restarts within rotation window.

        Args:
            force_new: Whether to generate a new session ID.
            consent_active: Whether telemetry consent is active.

        Returns:
            Anonymous session identifier string.
        """
        if not consent_active:
            return ""

        if force_new or self._current_session_id is None or self._is_expired():
            self._current_session_id = str(uuid4())
            self._created_timestamp = self._current_timestamp()
            self._save_session()

        return self._current_session_id

    async def rotate_session(self) -> str:
        """Rotate session, producing fresh identifier with no linkage.

        Returns:
            New session identifier string.
        """
        self._current_session_id = str(uuid4())
        self._created_timestamp = self._current_timestamp()
        self._save_session()
        logger.info("Telemetry session rotated")
        return self._current_session_id

    async def clear_session(self) -> None:
        """Clear session state (e.g., on consent withdrawal)."""
        self._current_session_id = None
        self._created_timestamp = None
        if self._session_file and os.path.exists(self._session_file):
            os.remove(self._session_file)
        logger.info("Telemetry session cleared")

    def _is_expired(self) -> bool:
        """Check if current session has exceeded rotation interval."""
        if self._created_timestamp is None or self._rotation_interval_seconds == 0:
            return False
        elapsed = self._current_timestamp() - self._created_timestamp
        return elapsed > self._rotation_interval_seconds

    def _load_session(self) -> None:
        """Load session from persisted state."""
        if not self._session_file or not os.path.exists(self._session_file):
            return
        try:
            with open(self._session_file, "r") as f:
                data = json.load(f)
            self._current_session_id = data.get("session_id")
            self._created_timestamp = data.get("created_at")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load session state: %s", e)

    def _save_session(self) -> None:
        """Persist session state."""
        if not self._session_file:
            return
        try:
            os.makedirs(os.path.dirname(self._session_file), exist_ok=True)
            with open(self._session_file, "w") as f:
                json.dump({
                    "session_id": self._current_session_id,
                    "created_at": self._created_timestamp,
                }, f)
        except OSError as e:
            logger.warning("Failed to persist session state: %s", e)

    def _current_timestamp(self) -> float:
        """Return current Unix timestamp."""
        import time
        return time.time()
