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

from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
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
    """Verifies actual liveness and classifies runtime state with staleness guard.

    FR-LAU-004 (Finding #12): PID reuse guard — verifies process identity matches
    persisted context by checking /proc/<pid>/cmdline for 'blender' on Linux.
    FR-LAU-004 (Finding #13): Stale state correction — updates persistence store
    when stale state is detected and reconciliation is enabled.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        liveness_checker: _LivenessChecker,
        pid_resolver: Callable[[], int | None],
        bridge_probe: _BridgeProbe | None = None,
        persisted_state_resolver: Callable[[], RuntimeStateVO | None] = lambda: None,
        stale_reconciliation_enabled: bool = True,
        state_corrector: PersistStateProtocol | None = None,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._is_alive = liveness_checker
        self._resolve_pid = pid_resolver
        self._bridge = bridge_probe
        self._resolve_persisted = persisted_state_resolver
        self._stale_reconcile = stale_reconciliation_enabled
        self._state_corrector = state_corrector
        self._events = event_sink
        self._launch_time: float | None = None

    # ─── Block 2: Public Contract ────────────────────────────
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """Verify actual process liveness and classify runtime state.

        FR-LAU-004 (Finding #12): PID reuse guard — when process is alive, verify
        it matches the persisted launch context by checking /proc/<pid>/cmdline
        for 'blender' on Linux systems.
        """
        pid = self._resolve_pid()
        if pid is None:
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

        alive = self._is_alive(pid)
        if not alive:
            persisted = self._resolve_persisted()
            if persisted is not None and persisted.process_id == pid:
                # PID is dead but matches persisted reference — stale state
                self._emit_stale(pid)
                if self._stale_reconcile and self._state_corrector is not None:
                    self._correct_stale_state()
                return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, process_id=pid, depth=depth)

        # PID reuse guard (Finding #12): verify process identity when alive
        if self._is_pid_reused(pid):
            persisted = self._resolve_persisted()
            if persisted is not None:
                self._emit_stale(pid)
                if self._stale_reconcile and self._state_corrector is not None:
                    self._correct_stale_state()
                return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)

        ready = True
        # Check bridge readiness at any depth when bridge endpoint is configured
        if self._bridge is not None:
            ready = self._bridge(timeout_seconds=1.0 if depth == ProbeDepth.LIGHTWEIGHT else 2.0)

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
        """Record launch time so uptime can be derived (called by launcher)."""
        self._launch_time = launch_time

    def _is_pid_reused(self, pid: int) -> bool:
        """FR-LAU-004 (Finding #12): Check if PID has been reused by a non-Blender process.

        On Linux, reads /proc/<pid>/cmdline to verify the process is actually Blender.
        Returns True if the process is NOT Blender (PID reuse detected).
        Returns False if process is Blender or platform detection fails (graceful degradation).
        """
        if pid <= 0:
            return False
        try:
            cmdline_path = f"/proc/{pid}/cmdline"
            if not os.path.exists(cmdline_path):
                return False
            with open(cmdline_path, "rb") as f:
                cmdline = f.read().decode("utf-8", errors="replace")
            # Check if the process command line contains 'blender'
            return "blender" not in cmdline.lower()
        except OSError:
            # Cannot read /proc — fall back to graceful degradation
            return False

    def _correct_stale_state(self) -> None:
        """FR-LAU-004 (Finding #13): Clear stale process reference from persistence.

        When stale state is detected and reconciliation is enabled, update the
        persistence store to clear the stale process reference.
        """
        if self._state_corrector is not None:
            with contextlib.suppress(Exception):
                self._state_corrector.persist(
                    RuntimeStateVO(
                        executable_path="",
                        process_id=None,
                        launch_timestamp=0.0,
                        bridge_endpoint=None,
                        last_status=RuntimeState.NOT_RUNNING,
                    )
                )

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
