"""State persistence capability — corruption-safe runtime state storage.

FR-LAU-005: Persist Runtime State
- Atomic/crash-safe writes (temp file + atomic rename)
- Structural validation on read; corrupt/missing content falls back to empty
- No secrets or authentication material are persisted
- Failures degrade gracefully to in-memory operation
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from typing import Callable

from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    PersistenceResultVO,
    RuntimeState,
    RuntimeStateVO,
)


def _coerce_status(value: object) -> RuntimeState:
    """Coerce a loaded status value into a RuntimeState enum safely."""
    if isinstance(value, RuntimeState):
        return value
    if isinstance(value, str):
        try:
            return RuntimeState(value)
        except ValueError:
            return RuntimeState.NOT_RUNNING
    return RuntimeState.NOT_RUNNING

logger = logging.getLogger("BlenderMCPServer")


class StatePersistence(PersistStateProtocol):
    """Concrete implementation for corruption-safe runtime state persistence.

    FR-LAU-005: Persists only non-secret fields. Writes are atomic via a temp
    file + ``os.replace``. Reads validate structure; any malformed content
    returns ``None`` with a warning rather than crashing.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, path_resolver: Callable[[], str | None] | None = None) -> None:
        self._path_resolver = path_resolver or (lambda: None)

    # ─── Block 2: Protocol Method Implementation ─────────────

    def persist(self, state: RuntimeStateVO) -> PersistenceResultVO:
        """Atomically persist runtime state; corrupt writes never leave partial files."""
        path = self._path_resolver()
        if not path:
            logger.warning("No persistence location resolved; operating in-memory only")
            return PersistenceResultVO(success=False, warnings=("no_persistence_location",))

        payload = {
            "executable_path": state.executable_path,
            "process_id": state.process_id,
            "launch_timestamp": state.launch_timestamp,
            "bridge_endpoint": state.bridge_endpoint,
            "last_status": state.last_status.value if hasattr(state.last_status, "value") else state.last_status,
        }

        try:
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(dir=directory or ".", suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_path, path)
            return PersistenceResultVO(success=True)
        except (OSError, ValueError, TypeError) as e:
            logger.warning("Persistence failed, continuing in-memory: %s", e)
            return PersistenceResultVO(success=False, warnings=(f"persist_failed:{e!r}",))

    def load(self) -> RuntimeStateVO | None:
        """Load persisted state, returning None on missing/corrupt content."""
        path = self._path_resolver()
        if not path or not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("state root is not a mapping")
            return RuntimeStateVO(
                executable_path=str(data.get("executable_path", "")),
                process_id=int(data["process_id"]) if data.get("process_id") is not None else None,
                launch_timestamp=float(data.get("launch_timestamp", 0.0)),
                bridge_endpoint=data.get("bridge_endpoint"),
                last_status=_coerce_status(data.get("last_status")),
            )
        except (OSError, ValueError, KeyError, TypeError) as e:
            logger.warning("Corrupt state file (%s); treating as empty: %s", path, e)
            return None

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def __repr__(self) -> str:
        return "StatePersistence()"
