"""Capabilities: Runtime status — FR-LAU-004.

Verifies true process liveness (not persisted state) and classifies runtime
state, guarding against PID reuse. Implements RuntimeStatusProtocol.

Liveness and process-info lookup are injected DI boundaries.
"""

from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)


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

    # ─── Block 2: Public Contract ────────────────────────────
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """Verify actual process liveness and classify runtime state."""
        start = time.monotonic()
        pid = self._resolve_pid()
        if pid is None:
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

        alive = self._is_alive(pid)
        if not alive:
            persisted = self._resolve_persisted()
            if persisted is not None and persisted.process_id == pid:
                if self._stale_reconcile:
                    try:
                        self._emit_stale(pid)
                    except Exception:
                        logger.warning("Failed to emit stale event for pid %d", pid, exc_info=True)
                return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, process_id=pid, depth=depth)

        ready = True
        if depth == ProbeDepth.FULL and self._bridge is not None:
            ready = self._bridge(timeout_seconds=1.0)

        state = RuntimeState.RUNNING_READY if ready else RuntimeState.RUNNING_UNRESPONSIVE
        uptime = (time.monotonic() - self._launch_time) if self._launch_time else None
        probe_duration_ms = (time.monotonic() - start) * 1000.0

        try:
            self._emit(
                LauncherLifecycleEvent(
                    event_category=LAUNCHER_EVENT_STATUS_CHECKED,
                    state_before=state,
                    state_after=state,
                    process_reference=str(pid),
                    reason_summary=f"status_check_depth={depth.value}",
                )
            )
        except Exception:
            logger.warning("Failed to emit status check event", exc_info=True)

        return RuntimeStatusVO(
            state=state,
            process_id=pid,
            ready=ready,
            uptime_seconds=uptime,
            depth=depth,
            probe_duration_ms=probe_duration_ms,
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def mark_launched(self, launch_time: float) -> None:
        """Record launch time so uptime can be derived (called by launcher)."""
        self._launch_time = launch_time

    def _emit_stale(self, pid: int) -> None:
        try:
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
        except Exception:
            logger.warning("Failed to emit stale state event for pid %d", pid, exc_info=True)
