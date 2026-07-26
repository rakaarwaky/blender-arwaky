"""Persist state capability — atomic state store with corruption resilience.

FR-LAU-005: Persist Runtime State
- Writes state to disk atomically (temp file + rename)
- Reads fall back to empty on corruption
- Stale process reference reconciliation at startup
- Ensures durability without blocking launch
"""

import json
import logging
import os
import tempfile
import time

from modules.shared.src.launcher.contract_persist_state_protocol import (
    PersistStateProtocol,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    PersistenceResultVO,
    RuntimeState,
    RuntimeStateVO,
)

logger = logging.getLogger("BlenderMCPServer")


class PersistStateExecutor(PersistStateProtocol):
    """Concrete implementation for atomic state persistence.

    FR-LAU-005: Atomic writes, corruption fallback, stale reconciliation.
    Ensures durability without blocking launch.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, state_dir: str | None = None) -> None:
        self._state_dir = state_dir or self._default_state_dir()
        self._state_path = os.path.join(self._state_dir, "runtime_state.json")

    # ─── Block 2: Protocol Method Implementation ─────────────

    def persist(self, state: RuntimeStateVO) -> PersistenceResultVO:
        """Persist runtime state atomically to disk.

        FR-LAU-005: Atomic write (temp + rename). Corruption fallback on read.
        """
        start_time = time.time()

        try:
            self._atomic_write(self._state_path, {
                "process_id": state.process_id,
                "ready": state.last_status == RuntimeState.RUNNING_READY,
                "bridge_endpoint": state.bridge_endpoint,
            })
            duration_ms = (time.time() - start_time) * 1000
            logger.debug("State persisted: pid=%s", state.process_id)
            return PersistenceResultVO(success=True)

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("State persistence failed: %s", e)
            return PersistenceResultVO(success=False)

    def load(self) -> RuntimeStateVO | None:
        """Load persisted state with corruption fallback.

        FR-LAU-005: On corrupt data, falls back to empty state.
        """
        try:
            if not os.path.exists(self._state_path):
                return None

            data = self._atomic_read(self._state_path)
            process_id = data.get("process_id")
            ready = bool(data.get("ready", False))
            bridge_endpoint = data.get("bridge_endpoint")

            logger.debug("State loaded: pid=%s, ready=%s", process_id, ready)
            return RuntimeStateVO(
                process_id=process_id,
                bridge_endpoint=bridge_endpoint,
                last_status=RuntimeState.RUNNING_READY if ready else RuntimeState.NOT_RUNNING,
            )

        except Exception as e:
            logger.warning("Failed to load state, falling back to empty: %s", e)
            return None

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _default_state_dir(self) -> str:
        """Return default state directory (XDG or temp)."""
        xdg_state = os.environ.get("XDG_STATE_HOME") or os.path.join(
            os.path.expanduser("~"), ".local", "state"
        )
        state_dir = os.path.join(xdg_state, "blender-mcp", "launcher")
        os.makedirs(state_dir, exist_ok=True)
        return state_dir

    def _atomic_write(self, path: str, data: dict) -> None:
        """Write atomically via temp file + rename."""
        dir_path = os.path.dirname(path)
        with tempfile.NamedTemporaryFile(
            mode="w", dir=dir_path, suffix=".tmp", delete=False
        ) as tmp:
            json.dump(data, tmp, default=str)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name

        os.replace(tmp_name, path)

    def _atomic_read(self, path: str) -> dict:
        """Read with JSON parsing."""
        with open(path, "r") as f:
            return json.load(f)

    def get_state_path(self) -> str:
        return self._state_path

    def __repr__(self) -> str:
        return f"PersistStateExecutor(path={self._state_path})"