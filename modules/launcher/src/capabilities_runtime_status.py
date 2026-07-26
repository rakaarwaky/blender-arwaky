"""Runtime status capability — verify true process liveness and staleness.

FR-LAU-004: Check Runtime Status
- Verifies actual process liveness via OS signals, not persisted state alone
- Classifies runtime state (not_running / running_ready / running_unresponsive / stale)
- Guards against PID reuse through bounded, read-only checks
- Reconciles stale persisted state where enabled
"""

from __future__ import annotations

import logging
import os
import time
from typing import Callable

from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RuntimeStatusChecker(RuntimeStatusProtocol):
    """Concrete implementation for runtime status verification.

    FR-LAU-004: Reads true liveness through injected ``liveness_checker`` and
    ``bridge_probe`` seams. Defaults use OS liveness signals so the capability
    is usable in production but fully testable without a live process.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        liveness_checker: Callable[[int], bool] | None = None,
        pid_resolver: Callable[[], int | None] | None = None,
        bridge_probe: Callable[[float], bool] | None = None,
        stale_threshold_seconds: float = 0.0,
    ) -> None:
        self._liveness_checker = liveness_checker or self._default_liveness
        self._pid_resolver = pid_resolver or (lambda: None)
        self._bridge_probe = bridge_probe or (lambda _to: True)
        self._stale_threshold_seconds = stale_threshold_seconds

    # ─── Block 2: Protocol Method Implementation ─────────────

    def check_status(self, depth: str = "lightweight") -> RuntimeStatusVO:
        """Verify actual liveness and classify runtime state.

        FR-LAU-004: Never trusts persisted state alone. A persisted PID that no
        longer matches a live process is classified STALE. Read-only except for
        stale-state reconciliation handled by the caller.
        """
        pid = self._pid_resolver()
        if pid is None:
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, process_id=None, ready=False)

        alive = self._safe_liveness(pid)
        if not alive:
            # Persisted reference points at a dead process → stale, not running.
            return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, ready=False, stale=True)

        # Alive. Bridge readiness only matters for full depth (avoid round-trip).
        if depth == "full":
            ready = self._safe_bridge_probe()
        else:
            ready = True

        state = RuntimeState.RUNNING_READY if ready else RuntimeState.RUNNING_UNRESPONSIVE
        return RuntimeStatusVO(state=state, process_id=pid, ready=ready)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _safe_liveness(self, pid: int) -> bool:
        try:
            return bool(self._liveness_checker(pid))
        except (ProcessLookupError, PermissionError, OSError):
            return False

    def _safe_bridge_probe(self) -> bool:
        try:
            return bool(self._bridge_probe(self._stale_threshold_seconds or 1.0))
        except Exception:
            return False

    @staticmethod
    def _default_liveness(pid: int) -> bool:
        """Default liveness via OS signal probe (no kill, ESRCH => dead)."""
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False

    def classify_persisted(self, persisted: RuntimeStateVO | None, live_pid: int | None) -> RuntimeState:
        """Classify a persisted record against the live process id (PID reuse guard)."""
        if persisted is None:
            return RuntimeState.NOT_RUNNING
        if live_pid is None:
            return RuntimeState.NOT_RUNNING
        if persisted.process_id != live_pid:
            return RuntimeState.STALE
        return persisted.last_status

    def __repr__(self) -> str:
        return "RuntimeStatusChecker()"
