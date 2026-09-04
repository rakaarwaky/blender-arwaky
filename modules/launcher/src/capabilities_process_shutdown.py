"""Capabilities: Process shutdown — FR-LAU-003.

Graceful shutdown first, escalating to force termination when allowed.
Idempotent for absent processes; reports termination method. Implements
ShutdownProtocol.

Security integration (per PRD + FR-SEC-005):
  - Emits SecurityAuditEventVO on shutdown failures and escalations

Signal sender and killer are injected DI boundaries.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_EVENT_APPLICATION_STOPPED,
    LAUNCHER_EVENT_SHUTDOWN_ESCALATION,
)
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ProbeDepth,
    RuntimeState,
    ShutdownOutcomeVO,
    TerminationMethod,
)
from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_vo import AuditSeverity, SecurityAuditEventVO, ViolationCategory
from modules.shared.src.security.utility_security_path import redact_path

from .utility_audit_dispatch import emit_audit_sync


class _SignalSender(Protocol):
    """Sends a graceful signal to a process. DI boundary."""

    def __call__(self, process_id: int) -> bool: ...


class _ProcessKiller(Protocol):
    """Force-kills a process. DI boundary."""

    def __call__(self, process_id: int) -> bool: ...


class ProcessShutdown(ShutdownProtocol):
    """Graceful-then-force shutdown of the Blender process."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        status_protocol: RuntimeStatusProtocol,
        signal_sender: _SignalSender | None = None,
        killer: _ProcessKiller | None = None,
        timeout_seconds: float = 10.0,
        force_enabled: bool = True,
        audit_event_sink: EmitAuditProtocol | None = None,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._status = status_protocol
        self._signal = signal_sender
        self._kill = killer
        self._timeout = timeout_seconds
        self._force_enabled = force_enabled
        self._audit_events = audit_event_sink
        self._events = event_sink

    # ─── Block 2: Public Contract ────────────────────────────
    def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownOutcomeVO:
        """Stop Blender gracefully, escalating to force when allowed."""
        current = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)

        if current.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
            self._emit(
                LAUNCHER_EVENT_APPLICATION_STOPPED,
                current.state,
                RuntimeState.NOT_RUNNING,
                method=TerminationMethod.NONE.value,
            )
            return ShutdownOutcomeVO(
                success=True, termination_method=TerminationMethod.NONE, final_state=RuntimeState.NOT_RUNNING
            )

        if current.process_id is None:
            return ShutdownOutcomeVO(success=False, error="Process id unknown for running instance")

        start = time.monotonic()
        method = TerminationMethod.GRACEFUL
        escalated = False

        if self._signal is not None and not force:
            self._signal(current.process_id)

        if not self._wait_exit(current.process_id):
            if (force or allow_escalation) and self._force_enabled and self._kill is not None:
                self._kill(current.process_id)
                escalated = True
                method = TerminationMethod.FORCE
                # FR-SEC-005: emit security audit event on force escalation
                self._emit_security_audit(ViolationCategory.POLICY_OVERRIDE, "force_termination")
                self._emit(
                    LAUNCHER_EVENT_SHUTDOWN_ESCALATION,
                    RuntimeState.STOPPING,
                    RuntimeState.NOT_RUNNING,
                    process_reference=str(current.process_id),
                )
            else:
                # FR-SEC-005: emit security audit event on graceful shutdown failure
                self._emit_security_audit(ViolationCategory.PERMISSION_DENIED, "graceful_shutdown_timeout")
                duration_ms = (time.monotonic() - start) * 1000.0
                return ShutdownOutcomeVO(
                    success=False,
                    termination_method=TerminationMethod.GRACEFUL,
                    duration_ms=duration_ms,
                    error="Graceful shutdown exceeded timeout; escalation disallowed",
                )

        duration_ms = (time.monotonic() - start) * 1000.0
        self._emit(
            LAUNCHER_EVENT_APPLICATION_STOPPED,
            RuntimeState.STOPPING,
            RuntimeState.NOT_RUNNING,
            process_reference=str(current.process_id),
            method=method.value,
        )
        return ShutdownOutcomeVO(
            success=True,
            termination_method=method,
            duration_ms=duration_ms,
            final_state=RuntimeState.NOT_RUNNING,
            escalated=escalated,
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _wait_exit(self, _process_id: int) -> bool:
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            st = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)
            if st.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                return True
            time.sleep(0.05)
        return False

    def _emit(
        self, category: str, before: RuntimeState, after: RuntimeState, process_reference: str = "", method: str = ""
    ) -> None:
        if self._events is not None:
            self._events(
                LauncherLifecycleEvent(
                    event_category=category,
                    state_before=before,
                    state_after=after,
                    process_reference=redact_path(process_reference),
                    method=method,
                )
            )

    def _emit_security_audit(self, violation: ViolationCategory, reason: str = "") -> None:
        """FR-SEC-005: emit security audit event for shutdown operations."""
        if self._audit_events is not None:
            emit_audit_sync(
                self._audit_events,
                SecurityAuditEventVO(
                    violation_category=violation,
                    operation_type="shutdown_operation",
                    source_feature="launcher",
                    target_metadata={"reason": redact_path(reason)},
                    severity=AuditSeverity.WARNING,
                ),
            )
