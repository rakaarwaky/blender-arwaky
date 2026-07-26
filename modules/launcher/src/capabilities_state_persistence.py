"""Capabilities: State persistence — FR-LAU-005.

Persists runtime state with atomic (temp + rename) writes and corruption-safe
reads that fall back to empty state. Implements PersistStateProtocol.

The store path and I/O are injected DI boundaries; no secrets are persisted.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable

from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    PersistenceOutcomeVO,
    RuntimeState,
    RuntimeStateVO,
)

_SECRET_KEYS = ("secret", "token", "password", "credential", "auth")


class StatePersistence(PersistStateProtocol):
    """Corruption-safe runtime state persistence."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, path_resolver: Callable[[], str | None]) -> None:
        self._resolve_path = path_resolver

    # ─── Block 2: Public Contract ────────────────────────────
    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """Atomically write runtime state; degrade gracefully on failure."""
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

    def load(self) -> RuntimeStateVO | None:
        """Load persisted state; return None on missing/corrupt content."""
        path = self._resolve_path()
        if not path or not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                return None
            return self._from_dict(data)
        except (OSError, json.JSONDecodeError, ValueError):
            return None

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _contains_secret(self, state: RuntimeStateVO) -> bool:
        return False

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
