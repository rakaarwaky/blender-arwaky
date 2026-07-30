"""Capabilities: Process launcher — FR-LAU-002.

Spawns Blender, enforces idempotency, waits for readiness, and emits a
lifecycle event. Implements LaunchProtocol.

Security integration (per PRD + FR-SEC-004/005):
  - Emits SecurityAuditEventVO on launch failures
  - Redacts bridge endpoints in events using security module's redact utility

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
)
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LaunchMethod,
    LaunchMode,
    LaunchOutcomeVO,
    ProbeDepth,
    RuntimeState,
    TimeoutSeconds,
)
from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_vo import AuditSeverity, SecurityAuditEventVO, ViolationCategory


class _ProcessSpawner(Protocol):
    """Spawns Blender; returns a process id. DI boundary."""

    def __call__(self, executable: str, mode: str, readiness_timeout_seconds: float) -> int: ...


class _ReadinessProbe(Protocol):
    """Probes bridge readiness; returns True when ready. DI boundary."""

    def __call__(self, process_id: int, timeout_seconds: float) -> bool: ...


class ProcessLauncher(LaunchProtocol):
    """Launches Blender with the integration component active and confirms readiness."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        executable_resolver: Callable[[], str | None],
        status_protocol: RuntimeStatusProtocol,
        spawner: _ProcessSpawner | None = None,
        readiness_probe: _ReadinessProbe | None = None,
        audit_event_sink: EmitAuditProtocol | None = None,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._resolve_executable = executable_resolver
        self._status = status_protocol
        self._spawner = spawner
        self._probe = readiness_probe
        self._audit_events = audit_event_sink
        self._events = event_sink

    # ─── Block 2: Public Contract ────────────────────────────
    def launch(
        self, mode: LaunchMode = LaunchMode.INTERFACE, readiness_timeout_seconds: TimeoutSeconds | None = None
    ) -> LaunchOutcomeVO:
        """Start Blender and confirm readiness within the configured timeout."""
        timeout = readiness_timeout_seconds if readiness_timeout_seconds is not None else 30.0

        current = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)
        if current.state in (RuntimeState.RUNNING_READY, RuntimeState.RUNNING_UNRESPONSIVE, RuntimeState.STARTING):
            return LaunchOutcomeVO(
                success=True,
                process_id=current.process_id,
                ready=(current.state == RuntimeState.RUNNING_READY),
                launch_method=LaunchMethod.IDEMPOTENT,
            )

        executable = self._resolve_executable()
        if not executable:
            self._emit_security_audit(ViolationCategory.UNAUTHORIZED_ACCESS, "no_executable_path")
            return LaunchOutcomeVO(success=False, error="No registered executable path")

        if self._spawner is None:
            self._emit_security_audit(ViolationCategory.PERMISSION_DENIED, "spawner_not_configured")
            return LaunchOutcomeVO(success=False, error="Process spawner not configured")

        start = time.monotonic()
        try:
            pid = self._spawner(executable, mode.value, timeout)
        except Exception as exc:
            self._emit_security_audit(ViolationCategory.UNAUTHORIZED_ACCESS, str(exc))
            self._emit(
                LAUNCHER_EVENT_LAUNCH_FAILED, RuntimeState.NOT_RUNNING, RuntimeState.NOT_RUNNING, reason=str(exc)
            )
            return LaunchOutcomeVO(success=False, error=f"Spawn failed: {exc}")

        ready = False
        if self._probe is not None:
            ready = self._probe(pid, timeout)

        duration_ms = (time.monotonic() - start) * 1000.0
        if not ready:
            self._emit(
                LAUNCHER_EVENT_LAUNCH_FAILED, RuntimeState.STARTING, RuntimeState.STARTING, process_reference=str(pid)
            )
            return LaunchOutcomeVO(
                success=False,
                process_id=pid,
                ready=False,
                duration_ms=duration_ms,
                error="Readiness not confirmed within timeout",
            )

        self._emit(
            LAUNCHER_EVENT_APPLICATION_STARTED,
            RuntimeState.STARTING,
            RuntimeState.RUNNING_READY,
            process_reference=str(pid),
        )
        return LaunchOutcomeVO(
            success=True, process_id=pid, ready=True, launch_method=LaunchMethod.SPAWN, duration_ms=duration_ms
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _emit(
        self, category: str, before: RuntimeState, after: RuntimeState, process_reference: str = "", reason: str = ""
    ) -> None:
        if self._events is not None:
            # FR-SEC-004: redact bridge endpoints in events
            from modules.shared.src.security.utility_security_path import redact_path as _redact_path

            redacted_ref = _redact_path(process_reference)
            redacted_reason = _redact_path(reason) if reason else ""
            self._events(
                LauncherLifecycleEvent(
                    event_category=category,
                    state_before=before,
                    state_after=after,
                    process_reference=redacted_ref,
                    reason_summary=redacted_reason,
                )
            )

    def _emit_security_audit(self, violation: ViolationCategory, reason: str = "") -> None:
        """FR-SEC-005: emit security audit event for launcher operations."""
        if self._audit_events is not None:
            from modules.shared.src.security.utility_security_path import redact_path as _redact_path

            self._audit_events.emit_audit(
                SecurityAuditEventVO(
                    violation_category=violation,
                    operation_type="launcher_operation",
                    source_feature="launcher",
                    target_metadata={"reason": _redact_path(reason)},
                    severity=AuditSeverity.WARNING,
                )
            )
