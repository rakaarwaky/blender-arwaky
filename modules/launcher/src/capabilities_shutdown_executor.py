"""Shutdown capability — graceful shutdown with force termination fallback.

FR-LAU-003: Shut Down Application
- Attempts graceful shutdown first
- Escalates to force termination when unresponsive
- Verifies true liveness after termination
- Idempotent: shutdown of absent process returns success
"""

import logging
import time
from collections.abc import Callable

from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    RuntimeState,
    ShutdownOutcomeVO,
)

logger = logging.getLogger("BlenderMCPServer")


def _default_signal_sender(pid: int, sig: int) -> bool:
    import os

    try:
        os.kill(pid, sig)
        return True
    except (ProcessLookupError, OSError):
        return False


def _default_liveness(pid: int) -> bool:
    import os

    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, OSError):
        return False


class ShutdownExecutor(ShutdownProtocol):
    """Concrete implementation for graceful-then-force shutdown.

    FR-LAU-003: Graceful first, escalates to force when unresponsive.
    Verifies true liveness after termination. Idempotent for absent process.
    Process signalling is injected for deterministic testing.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        signal_sender: Callable[[int, int], bool] | None = None,
        liveness: Callable[[int], bool] | None = None,
        shutdown_timeout_seconds: float = 10.0,
        force_enabled: bool = True,
        pid_resolver: Callable[[], int | None] | None = None,
        on_stopped: Callable[[], None] | None = None,
    ) -> None:
        self._signal_sender = signal_sender or _default_signal_sender
        self._liveness = liveness or _default_liveness
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._force_enabled = force_enabled
        self._pid_resolver = pid_resolver
        self._on_stopped = on_stopped
        self._process_id: int | None = None

    # ─── Block 2: Protocol Method Implementation ─────────────

    def shutdown(
        self,
        force: bool = False,
        allow_escalation: bool = True,
    ) -> ShutdownOutcomeVO:
        """Stop Blender gracefully, escalating to force termination when allowed.

        FR-LAU-003: Graceful first, escalates to force when unresponsive.
        Verifies true liveness after termination. Idempotent for absent process.
        """
        start_time = time.time()

        pid = self._pid_resolver() if self._pid_resolver is not None else self._process_id
        if pid is None or not self._liveness(pid):
            logger.info("Process not running — shutdown is a no-op")
            self._notify_stopped()
            return ShutdownOutcomeVO(
                success=True, termination_method="none", duration_ms=0.0,
                final_state=RuntimeState.NOT_RUNNING, escalated=False,
            )

        try:
            logger.info("Initiating graceful shutdown")
            self._signal_sender(pid, 15)  # SIGTERM
            graceful_succeeded = self._wait_for_exit(self._shutdown_timeout_seconds)

            if graceful_succeeded:
                duration_ms = (time.time() - start_time) * 1000
                logger.info("Graceful shutdown completed")
                self._notify_stopped()
                return ShutdownOutcomeVO(
                    success=True, termination_method="graceful",
                    duration_ms=duration_ms, final_state=RuntimeState.NOT_RUNNING,
                    escalated=False,
                )

            if allow_escalation and self._force_enabled and not force:
                logger.warning("Graceful shutdown timed out — escalating to force")
                self._signal_sender(pid, 9)  # SIGKILL
                verified = not self._liveness(pid)
                duration_ms = (time.time() - start_time) * 1000
                logger.info("Force termination completed and verified")
                self._notify_stopped()
                return ShutdownOutcomeVO(
                    success=verified, termination_method="force",
                    duration_ms=duration_ms,
                    final_state=RuntimeState.NOT_RUNNING if verified else RuntimeState.RUNNING_UNRESPONSIVE,
                    escalated=True,
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.warning("Graceful shutdown timed out and force escalation disallowed")
            return ShutdownOutcomeVO(
                success=False, termination_method="none", duration_ms=duration_ms,
                final_state=RuntimeState.RUNNING_UNRESPONSIVE, escalated=False,
                error="Graceful shutdown timed out and force escalation is disallowed",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Shutdown failed: %s", e)
            return ShutdownOutcomeVO(
                success=False, termination_method="none", duration_ms=duration_ms,
                final_state=RuntimeState.RUNNING_UNRESPONSIVE, escalated=False,
                error=str(e),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _wait_for_exit(self, timeout_seconds: float) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if not self._liveness(self._pid_for_check()):
                return True
            time.sleep(0.1)
        return False

    def _pid_for_check(self) -> int:
        pid = self._pid_resolver() if self._pid_resolver is not None else self._process_id
        if pid is None:
            return -1
        return pid

    def _notify_stopped(self) -> None:
        if self._on_stopped is not None:
            try:
                self._on_stopped()
            except Exception:
                pass

    def set_process_id(self, pid: int | None) -> None:
        """Record the active process id (wired by the orchestrator)."""
        self._process_id = pid

    def __repr__(self) -> str:
        state = "running" if (self._process_id is not None and self._liveness(self._process_id)) else "stopped"
        return f"ShutdownExecutor(state={state}, id={self._process_id})"
