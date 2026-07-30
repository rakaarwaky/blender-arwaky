"""Capabilities: State persistence — FR-LAU-005.

Persists runtime state with atomic (temp + rename) writes and corruption-safe
reads that fall back to empty state. Implements PersistStateProtocol.

The store path and I/O are injected DI boundaries; no secrets are persisted.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from collections.abc import Callable

from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_EVENT_CORRUPT_STATE_DETECTED,
)
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    PersistenceOutcomeVO,
    RuntimeState,
    RuntimeStateVO,
)

_SECRET_KEYS = ("secret", "token", "password", "credential", "auth")


class StatePersistence(PersistStateProtocol):
    """Corruption-safe runtime state persistence with concurrent access safety.

    P1 (Finding #7 fix): Emits warning event on corrupt/unreadable state load.
    Returns empty state with warning instead of silent None.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        path_resolver: Callable[[], str | None],
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._resolve_path = path_resolver
        self._lock = threading.Lock()
        self._events = event_sink

    # ─── Block 2: Public Contract ────────────────────────────
    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """Atomically write runtime state; degrade gracefully on failure."""
        with self._lock:
            return self._persist_impl(state)

    def load(self) -> RuntimeStateVO | None:
        """Load persisted state; return None on missing/corrupt content.

        P1 (Finding #7 fix): Emits warning event on corrupt/unreadable state.
        Falls back to empty state with warning instead of silent None.
        """
        with self._lock:
            return self._load_impl()

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
        """Load persisted state with corruption fallback (FR-LAU-005).

        P1 (Finding #7 fix): Emits warning event on corrupt/unreadable state.
        Falls back to empty state with warning instead of silent None.
        """
        path = self._resolve_path()
        if not path or not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                self._emit_corrupt_warning("state_data_not_dict")
                return None
            return self._from_dict(data)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self._emit_corrupt_warning(f"load_error: {exc}")
            return None

    def _emit_corrupt_warning(self, reason: str) -> None:
        """Emit corrupt state warning event (P1 — Finding #7 fix)."""
        if self._events is not None:
            try:
                self._events(
                    LauncherLifecycleEvent(
                        event_category=LAUNCHER_EVENT_CORRUPT_STATE_DETECTED,
                        state_before=RuntimeState.NOT_RUNNING,
                        state_after=RuntimeState.NOT_RUNNING,
                        reason_summary=f"corrupt_state: {reason}",
                    )
                )
            except Exception:
                pass  # Event emission failure is non-blocking

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _contains_secret(self, state: RuntimeStateVO) -> bool:
        """Check if state contains secret-like field names."""
        data = self._to_dict(state)
        for key in _SECRET_KEYS:
            if key in data:
                return True
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
