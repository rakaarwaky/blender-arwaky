"""Capability: Telemetry session manager.

FR-TLM-003: Manages anonymous session identifiers with persistence,
rotation, and consent withdrawal support.

Implements TelemetrySessionProtocol — sync protocol with file-based
persistence and consent-aware session retrieval.
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import (
    EnabledFlag,
    FilePath,
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetrySessionManager(TelemetrySessionProtocol):
    def __init__(self, persistence_path: FilePath) -> None:
        self._session_id: SessionId | None = None
        self._persistence_path = Path(str(persistence_path))
        self._lock = threading.Lock()

    def get_session_id(self, consent_active: EnabledFlag) -> SessionId | None:
        if not consent_active:
            return None

        with self._lock:
            if self._session_id is None:
                self._session_id = self._load_or_generate()
            return self._session_id

    def initialize_session(self) -> SuccessFlag:
        with self._lock:
            self._session_id = SessionId(str(uuid.uuid4()))
            self._persist()
            return SuccessFlag(True)

    def rotate_session(self) -> SessionId:
        with self._lock:
            self._session_id = SessionId(str(uuid.uuid4()))
            self._persist()
            return self._session_id

    def clear_session(self) -> None:
        with self._lock:
            self._session_id = None
            self._delete_persistence()

    def _load_or_generate(self) -> SessionId:
        try:
            if self._persistence_path.exists():
                data = json.loads(self._persistence_path.read_text())
                return SessionId(str(data["session_id"]))
        except Exception as exc:
            logger.warning("Failed to load telemetry session: %s", exc)

        return SessionId(str(uuid.uuid4()))

    def _persist(self) -> None:
        try:
            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            self._persistence_path.write_text(json.dumps({"session_id": str(self._session_id)}))
        except OSError as exc:
            logger.warning("Failed to persist telemetry session: %s", exc)

    def _delete_persistence(self) -> None:
        try:
            if self._persistence_path.exists():
                self._persistence_path.unlink()
        except OSError as exc:
            logger.warning("Failed to delete telemetry session: %s", exc)
