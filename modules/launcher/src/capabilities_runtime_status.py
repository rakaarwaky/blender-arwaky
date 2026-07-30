"""Capabilities: Runtime status — FR-LAU-004.

Verifies true process liveness (not persisted state) and classifies runtime
state, guarding against PID reuse. Implements RuntimeStatusProtocol.

Liveness and process-info lookup are injected DI boundaries.
"""

from __future__ import annotations

import contextlib
import os
import time
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_EVENT_STALE_STATE_DETECTED,
    LAUNCHER_EVENT_STATUS_CHECKED,
)
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ProbeDepth,
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
)


class _LivenessChecker(Protocol):
    """Returns True if the pid is actually alive. DI boundary."""

    def __call__(self, process_id: int) -> bool:
        ...


class _BridgeProbe(Protocol):
    """Returns True if the bridge endpoint is responsive. DI boundary."""

    def __call__(self, timeout_seconds: float) -> bool:
        ...


class RuntimeStatusChecker(RuntimeStatusProtocol):
    """Verifies actual liveness and classifies runtime state with staleness guard."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        liveness_checker: _LivenessChecker,
        pid_resolver: Callable[[], int | None],
        bridge_probe: _BridgeProbe | None = None,
        persisted_state_resolver: Callable[[], RuntimeStateVO | None] = lambda: None,
        stale_reconciliation_enabled: bool = True,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._is_alive = liveness_checker
        self._resolve_pid = pid_resolver
        self._bridge = bridge_probe
        self._resolve_persisted = persisted_state_resolver
        self._stale_reconcile = stale_reconciliation_enabled
        self._events = event_sink
        self._launch_time: float | None = None

    # ─── Block 2: Public Contract ────────────────────────────
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """Verify actual process liveness and classify runtime state."""
        pid = self._resolve_pid()
        if pid is None:
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

        alive = self._is_alive(pid)
        if alive and self._is_pid_reused(pid):
            if self._stale_reconcile:
                self._emit_stale(pid)
            return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)

        if not alive:
            persisted = self._resolve_persisted()
            if persisted is not None and persisted.process_id == pid:
                if self._stale_reconcile:
                    self._emit_stale(pid)
                return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, process_id=pid, depth=depth)

        ready = True
        if depth == ProbeDepth.FULL and self._bridge is not None:
            ready = self._bridge(timeout_seconds=1.0)

        state = RuntimeState.RUNNING_READY if ready else RuntimeState.RUNNING_UNRESPONSIVE
        uptime = (time.monotonic() - self._launch_time) if self._launch_time else None

        if self._events is not None:
            self._events(LauncherLifecycleEvent(
                event_category=LAUNCHER_EVENT_STATUS_CHECKED,
                state_before=state,
                state_after=state,
                process_reference=str(pid),
                reason_summary=f"status_check_depth={depth.value}",
            ))

        return RuntimeStatusVO(state=state, process_id=pid, ready=ready, uptime_seconds=uptime, depth=depth)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def mark_launched(self, launch_time: float) -> None:
        """Record launch time so uptime can be derived (called by launcher)."""
        self._launch_time = launch_time

    def _is_pid_reused(self, pid: int) -> bool:
        stat_path = f"/proc/{pid}/stat"
        if not os.path.exists(stat_path):
            return False
        with contextlib.suppress(OSError, ValueError):
            with open(stat_path, encoding="utf-8") as fh:
                content = fh.read().strip()
            rparen = content.rfind(")")
            if rparen == -1:
                return False
            fields = content[rparen + 1 :].split()
            if len(fields) > 19:
                start_ticks = float(fields[19])
                stored_ticks = getattr(self, "_stored_proc_start_ticks", None)
                if stored_ticks is not None:
                    return abs(start_ticks - stored_ticks) > 0.01
                if self._launch_time is not None:
                    return True
                self._stored_proc_start_ticks = start_ticks
        return False

    def _emit_stale(self, pid: int) -> None:
        if self._events is not None:
            self._events(LauncherLifecycleEvent(
                event_category=LAUNCHER_EVENT_STALE_STATE_DETECTED,
                state_before=RuntimeState.RUNNING_READY, state_after=RuntimeState.STALE,
                process_reference=str(pid), reason_summary="stale_state_detected",
            ))
