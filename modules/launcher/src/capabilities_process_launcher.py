"""Capabilities: Process launcher — FR-LAU-002.

Spawns Blender, enforces idempotency, waits for readiness, and emits a
lifecycle event. Implements LaunchProtocol.

The actual spawn and readiness probe are injected (DI boundaries) so the
logic is testable without launching a real Blender process.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_EVENT_APPLICATION_STARTED,
    LAUNCHER_EVENT_LAUNCH_FAILED,
    LAUNCHER_MODE_INTERFACE,
)
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LaunchResultVO,
    RuntimeState,
)


class _ProcessSpawner(Protocol):
    """Spawns Blender; returns a process id. DI boundary."""

    def __call__(self, executable: str, mode: str, readiness_timeout_seconds: float) -> int:
        ...


class _ReadinessProbe(Protocol):
    """Probes bridge readiness; returns True when ready. DI boundary."""

    def __call__(self, process_id: int, timeout_seconds: float) -> bool:
        ...


class ProcessLauncher(LaunchProtocol):
    """Launches Blender with the integration component active and confirms readiness."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        executable_resolver: Callable[[], str | None],
        status_protocol: RuntimeStatusProtocol,
        spawner: _ProcessSpawner | None = None,
        readiness_probe: _ReadinessProbe | None = None,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._resolve_executable = executable_resolver
        self._status = status_protocol
        self._spawner = spawner
        self._probe = readiness_probe
        self._events = event_sink

    # ─── Block 2: Public Contract ────────────────────────────
    def launch(self, mode: str = LAUNCHER_MODE_INTERFACE, readiness_timeout_seconds: float | None = None) -> LaunchResultVO:
        """Start Blender and confirm readiness within the configured timeout."""
        timeout = readiness_timeout_seconds if readiness_timeout_seconds is not None else 30.0

        current = self._status.check_status(depth="lightweight")
        if current.state in (RuntimeState.RUNNING_READY, RuntimeState.RUNNING_UNRESPONSIVE, RuntimeState.STARTING):
            return LaunchResultVO(
                success=True,
                process_id=current.process_id,
                ready=(current.state == RuntimeState.RUNNING_READY),
                launch_method="idempotent",
            )

        executable = self._resolve_executable()
        if not executable:
            return LaunchResultVO(success=False, error="No registered executable path")

        if self._spawner is None:
            return LaunchResultVO(success=False, error="Process spawner not configured")

        start = time.monotonic()
        try:
            pid = self._spawner(executable, mode, timeout)
        except Exception as exc:
            self._emit(LAUNCHER_EVENT_LAUNCH_FAILED, RuntimeState.NOT_RUNNING, RuntimeState.NOT_RUNNING, reason=str(exc))
            return LaunchResultVO(success=False, error=f"Spawn failed: {exc}")

        ready = False
        if self._probe is not None:
            ready = self._probe(pid, timeout)

        duration_ms = (time.monotonic() - start) * 1000.0
        if not ready:
            self._emit(LAUNCHER_EVENT_LAUNCH_FAILED, RuntimeState.STARTING, RuntimeState.STARTING, process_reference=str(pid))
            return LaunchResultVO(
                success=False, process_id=pid, ready=False,
                duration_ms=duration_ms, error="Readiness not confirmed within timeout",
            )

        self._emit(LAUNCHER_EVENT_APPLICATION_STARTED, RuntimeState.STARTING, RuntimeState.RUNNING_READY, process_reference=str(pid))
        return LaunchResultVO(success=True, process_id=pid, ready=True, launch_method="spawn", duration_ms=duration_ms)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _emit(self, category: str, before: RuntimeState, after: RuntimeState, process_reference: str = "", reason: str = "") -> None:
        if self._events is not None:
            self._events(LauncherLifecycleEvent(
                event_category=category, state_before=before, state_after=after,
                process_reference=process_reference, reason_summary=reason,
            ))