"""Capabilities: Process shutdown — FR-LAU-003.

Graceful shutdown first, escalating to force termination when allowed.
Idempotent for absent processes; reports termination method. Implements
ShutdownProtocol.

P0: Updated to accept ShutdownRequestVO instead of primitive parameters.
Signal sender and killer are injected DI boundaries.

P0: Integrates PersistStateProtocol for internal state persistence after termination.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
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
    RuntimeStateVO,
    ShutdownOutcomeVO,
    ShutdownRequestVO,
    TerminationMethod,
)
from modules.shared.src.security.utility_security_redactor import redact_sensitive

logger = logging.getLogger("BlenderMCPServer")


class _SignalSender(Protocol):
    """Sends a graceful signal to a process. DI boundary."""

    def __call__(self, process_id: int) -> bool: ...


class _ProcessKiller(Protocol):
    """Force-kills a process. DI boundary."""

    def __call__(self, process_id: int) -> bool: ...


class ProcessShutdown(ShutdownProtocol):
    """Graceful-then-force shutdown of the Blender process.

    P0: Accepts ShutdownRequestVO in shutdown() method.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        status_protocol: RuntimeStatusProtocol,
        persist_cap: PersistStateProtocol | None = None,
        signal_sender: _SignalSender | None = None,
        killer: _ProcessKiller | None = None,
        timeout_seconds: float = 10.0,
        force_enabled: bool = True,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._status = status_protocol
        self._persist = persist_cap
        self._signal = signal_sender
        self._kill = killer
        self._timeout = timeout_seconds
        self._force_enabled = force_enabled
        self._events = event_sink
        self._lock = threading.Lock()

    # ─── Block 2: Public Contract ────────────────────────────
    def shutdown(self, request: ShutdownRequestVO) -> ShutdownOutcomeVO:
        """Stop Blender gracefully, escalating to force when allowed.

        P0: Accepts ShutdownRequestVO instead of primitive parameters.
        Extracts force_requested and escalation_confirmed from the request VO.
        """
        with self._lock:
            force = request.force_requested
            allow_escalation = request.escalation_confirmed

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
                    self._emit(
                        LAUNCHER_EVENT_SHUTDOWN_ESCALATION,
                        RuntimeState.STOPPING,
                        RuntimeState.NOT_RUNNING,
                        process_reference=str(current.process_id),
                    )
                    # Post-kill verification: confirm process is dead after SIGKILL
                    self._wait_exit(current.process_id, verify_after_timeout=True)
                else:
                    duration_ms = (time.monotonic() - start) * 1000.0
                    return ShutdownOutcomeVO(
                        success=False,
                        termination_method=TerminationMethod.GRACEFUL,
                        duration_ms=duration_ms,
                        error="Graceful shutdown exceeded timeout; escalation disallowed",
                    )

            duration_ms = (time.monotonic() - start) * 1000.0

            # Post-termination persistence: record NOT_RUNNING state
            if self._persist is not None:
                try:
                    self._persist.persist(
                        RuntimeStateVO(
                            executable_path="",
                            process_id=None,
                            launch_timestamp=0.0,
                            bridge_endpoint=None,
                            last_status=RuntimeState.NOT_RUNNING,
                        )
                    )
                except Exception as exc:
                    logger.warning("Failed to persist state after shutdown: %s", exc)

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
    def _wait_exit(self, process_id: int, verify_after_timeout: bool = False) -> bool:
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            st = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)
            if st.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                return True
            time.sleep(0.05)

        # Post-kill verification: after timeout/escalation, verify process is actually dead
        if verify_after_timeout:
            st = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)
            if st.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                return True

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
                    process_reference=redact_sensitive(process_reference),
                    method=method,
                )
            )
