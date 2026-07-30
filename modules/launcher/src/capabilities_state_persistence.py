"""Capabilities: State persistence — FR-LAU-005.

Persists runtime state with atomic (temp + rename) writes and corruption-safe
reads that fall back to empty state. Implements PersistStateProtocol.

The store path and I/O are injected DI boundaries; no secrets are persisted.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
from collections.abc import Callable

from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LoadOutcomeVO,
    PersistenceOutcomeVO,
    RuntimeState,
    RuntimeStateVO,
)

logger = logging.getLogger(__name__)

_SECRET_KEYS = ("secret", "token", "password", "credential", "auth")


class StatePersistence(PersistStateProtocol):
    """Corruption-safe runtime state persistence with concurrent access safety."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, path_resolver: Callable[[], str | None]) -> None:
        self._resolve_path = path_resolver
        self._lock = threading.Lock()

    # ─── Block 2: Public Contract ────────────────────────────
    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """Atomically write runtime state; degrade gracefully on failure."""
        with self._lock:
            return self._persist_impl(state)

    def load(self) -> RuntimeStateVO | None:
        """Load persisted state; return None on missing/corrupt content."""
        with self._lock:
            return self._load_impl()

    def load_with_warnings(self) -> LoadOutcomeVO:
        """Load persisted state with corruption/parse warnings (FR-LAU-005)."""
        with self._lock:
            return self._load_with_warnings_impl()

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _persist_impl(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """Atomic write with secret detection (FR-LAU-005)."""
        warnings: list[str] = []
        if self._contains_secret(state):
            warnings.append("state contained secret-like field; not persisted")

        path = self._resolve_path()
        if not path:
            return PersistenceOutcomeVO(success=False, warnings=tuple(warnings + ["no persistence location"]))

        payload = self._to_dict(state)
        try:
            self._atomic_write(path, payload)
            return PersistenceOutcomeVO(success=True, warnings=tuple(warnings))
        except OSError as exc:
            warnings.append(f"persistence failed: {exc}")
            return PersistenceOutcomeVO(success=False, warnings=tuple(warnings))

    def _load_impl(self) -> RuntimeStateVO | None:
        """Load persisted state with corruption fallback (FR-LAU-005)."""
        path = self._resolve_path()
        if not path or not os.path.exists(path):
            return None
        try:
            return self._from_dict_impl(path)
        except (OSError, json.JSONDecodeError, ValueError):
            return None

    def _load_with_warnings_impl(self) -> LoadOutcomeVO:
        """Load persisted state with corruption/parse warnings."""
        path = self._resolve_path()
        if not path or not os.path.exists(path):
            return LoadOutcomeVO(state=None, warnings=(), corrupted=False)

        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            return self._from_dict_with_warnings(data)
        except (OSError, json.JSONDecodeError, ValueError):
            return LoadOutcomeVO(state=None, warnings=("corrupted or malformed state file",), corrupted=True)

    def _from_dict_impl(self, path: str) -> RuntimeStateVO | None:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError, ValueError):
            return None

        if not isinstance(data, dict):
            return None

        try:
            state = self._from_dict(data)
        except Exception:
            return None

        return state

    def _from_dict_with_warnings(self, data: dict) -> LoadOutcomeVO:
        warnings: list[str] = []

        if not isinstance(data, dict):
            return LoadOutcomeVO(state=None, warnings=("state is not a JSON object",), corrupted=True)

        # Validate expected fields
        for key in ("executable_path", "process_id", "launch_timestamp", "bridge_endpoint", "last_status"):
            if key not in data:
                warnings.append(f"missing field: {key}")

        try:
            state = self._from_dict(data)
        except ValueError as exc:
            warnings.append(f"parse error: {exc}")
            return LoadOutcomeVO(state=None, warnings=tuple(warnings), corrupted=True)

        return LoadOutcomeVO(state=state, warnings=tuple(warnings), corrupted=len(warnings) > 0)

    def _contains_secret(self, state: RuntimeStateVO) -> bool:
        """Check if state contains secret-like field names."""
        data = self._to_dict(state)
        return any(key in data for key in _SECRET_KEYS)

    def _to_dict(self, state: RuntimeStateVO) -> dict:
        return {
            "executable_path": state.executable_path,
            "process_id": state.process_id,
            "launch_timestamp": state.launch_timestamp,
            "bridge_endpoint": state.bridge_endpoint,
            "last_status": state.last_status.value if hasattr(state.last_status, "value") else str(state.last_status),
        }

    def _from_dict(self, data: dict) -> RuntimeStateVO:
        last = data.get("last_status", "not_running")
        try:
            last_state = RuntimeState(last)
        except ValueError:
            logger.warning("Invalid last_status value '%s', falling back to NOT_RUNNING", last)
            last_state = RuntimeState.NOT_RUNNING
        return RuntimeStateVO(
            executable_path=data.get("executable_path", ""),
            process_id=data.get("process_id"),
            launch_timestamp=float(data.get("launch_timestamp", 0.0)),
            bridge_endpoint=data.get("bridge_endpoint"),
            last_status=last_state,
        )

    def _atomic_write(self, path: str, payload: dict) -> None:
        directory = os.path.dirname(path) or "."
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
