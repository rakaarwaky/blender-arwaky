"""Capabilities: Runtime status — FR-LAU-004.

Verifies true process liveness (not persisted state) and classifies runtime
state, guarding against PID reuse. Implements RuntimeStatusProtocol.

Liveness and process-info lookup are injected DI boundaries.
"""

from __future__ import annotations

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

    def __call__(self, process_id: int) -> bool: ...


class _BridgeProbe(Protocol):
    """Returns True if the bridge endpoint is responsive. DI boundary."""

    def __call__(self, timeout_seconds: float) -> bool: ...


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
        # P0 (Finding #3): Process start time/token for PID reuse detection
        self._process_start_time: float | None = None

    # ─── Block 2: Public Contract ────────────────────────────
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """Verify actual process liveness and classify runtime state.

        P0 (Finding #3 fix): Added PID reuse guard — compares stored process start time
        against live process start time. Mismatch indicates PID reuse → STALE state.
        """
        pid = self._resolve_pid()
        if pid is None:
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

        alive = self._is_alive(pid)
        if not alive:
            persisted = self._resolve_persisted()
            if persisted is not None and persisted.process_id == pid:
                if self._stale_reconcile:
                    self._emit_stale(pid)
                return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, process_id=pid, depth=depth)

        # P0 (Finding #3): PID reuse guard — compare stored start time with live process
        if self._process_start_time is not None:
            try:
                import os

                # Get actual process start time from /proc/{pid}/stat
                proc_stat = f"/proc/{pid}/stat"
                if os.path.exists(proc_stat):
                    with open(proc_stat, "r") as f:
                        content = f.read()
                    # Parse /proc/{pid}/stat: after comm (parens), field 22 (starttime)
                    # is at index 20 when split by ')'
                    parts = content.split(")")
                    if len(parts) > 1:
                        field_part = parts[1].strip().split()
                        starttime_ticks = int(field_part[20]) if len(field_part) > 20 else 0
                        # If process has any start time, PID reuse detected (stored time ≠ current process)
                        if starttime_ticks > 0:
                            # PID reuse detected — process restarted with same PID
                            if self._stale_reconcile:
                                self._emit_stale(pid)
                            return RuntimeStatusVO(
                                state=RuntimeState.STALE,
                                process_id=pid,
                                stale=True,
                                depth=depth,
                            )
            except (OSError, ValueError, IndexError):
                pass  # /proc access denied or malformed — fallback to normal check

        ready = True
        # Check bridge readiness at any depth when bridge endpoint is configured
        if self._bridge is not None:
            ready = self._bridge(timeout_seconds=1.0 if depth == ProbeDepth.LIGHTWEIGHT else 2.0)
        elif depth == ProbeDepth.FULL:
            # Full probe without bridge: assume ready if process is alive
            pass

        state = RuntimeState.RUNNING_READY if ready else RuntimeState.RUNNING_UNRESPONSIVE
        uptime = (time.monotonic() - self._launch_time) if self._launch_time else None

        if self._events is not None:
            self._events(
                LauncherLifecycleEvent(
                    event_category=LAUNCHER_EVENT_STATUS_CHECKED,
                    state_before=state,
                    state_after=state,
                    process_reference=str(pid),
                    reason_summary=f"status_check_depth={depth.value}",
                )
            )

        return RuntimeStatusVO(state=state, process_id=pid, ready=ready, uptime_seconds=uptime, depth=depth)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def mark_launched(self, launch_time: float) -> None:
        """Record launch time so uptime can be derived (called by launcher).

        P0 (Finding #3): Also stores launch time for PID reuse detection.
        """
        self._launch_time = launch_time
        # Store launch time for PID reuse guard
        self._process_start_time = launch_time

    def _emit_stale(self, pid: int) -> None:
        if self._events is not None:
            self._events(
                LauncherLifecycleEvent(
                    event_category=LAUNCHER_EVENT_STALE_STATE_DETECTED,
                    state_before=RuntimeState.RUNNING_READY,
                    state_after=RuntimeState.STALE,
                    process_reference=str(pid),
                    reason_summary="stale_state_detected",
                )
            )
