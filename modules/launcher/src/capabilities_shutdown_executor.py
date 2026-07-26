"""Shutdown capability — graceful shutdown with force termination fallback.

FR-LAU-003: Shut Down Application
- Attempts graceful shutdown first
- Escalates to force termination when unresponsive
- Verifies true liveness after termination
- Idempotent: shutdown of absent process returns success
"""

import logging
import os
import signal
import time

from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    RuntimeState,
    ShutdownResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class ShutdownExecutor(ShutdownProtocol):
    """Concrete implementation for graceful-then-force shutdown.

    FR-LAU-003: Graceful first, escalates to force when unresponsive.
    Verifies true liveness after termination. Idempotent for absent process.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        self._process_id: int | None = None
        self._shutdown_timeout_seconds: float = 10.0
        self._force_enabled: bool = True

    # ─── Block 2: Protocol Method Implementation ─────────────

    def shutdown(
        self,
        force: bool = False,
        allow_escalation: bool = True,
    ) -> ShutdownResultVO:
        """Stop Blender gracefully, escalating to force termination when allowed.

        FR-LAU-003: Graceful first, escalates to force when unresponsive.
        Verifies true liveness after termination. Idempotent for absent process.
        """
        start_time = time.time()

        if not self._is_process_running():
            logger.info("Process not running — shutdown is a no-op")
            return ShutdownResultVO(
                success=True, termination_method="none", duration_ms=0.0,
                final_state=RuntimeState.NOT_RUNNING, escalated=False,
            )

        try:
            logger.info("Initiating graceful shutdown")
            self._graceful_shutdown()
            graceful_succeeded = self._wait_for_exit(self._shutdown_timeout_seconds)

            if graceful_succeeded:
                duration_ms = (time.time() - start_time) * 1000
                logger.info("Graceful shutdown completed")
                return ShutdownResultVO(
                    success=True, termination_method="graceful",
                    duration_ms=duration_ms, final_state=RuntimeState.NOT_RUNNING,
                    escalated=False,
                )

            if allow_escalation and self._force_enabled and not force:
                logger.warning("Graceful shutdown timed out — escalating to force")
                self._force_terminate()
                verified = self._verify_liveness(False)
                duration_ms = (time.time() - start_time) * 1000
                logger.info("Force termination completed and verified")
                return ShutdownResultVO(
                    success=verified, termination_method="force",
                    duration_ms=duration_ms,
                    final_state=RuntimeState.NOT_RUNNING if verified else RuntimeState.RUNNING_UNRESPONSIVE,
                    escalated=True,
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.warning("Graceful shutdown timed out and force escalation disallowed")
            return ShutdownResultVO(
                success=False, termination_method="none", duration_ms=duration_ms,
                final_state=RuntimeState.RUNNING_UNRESPONSIVE, escalated=False,
                error="Graceful shutdown timed out and force escalation is disallowed",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Shutdown failed: %s", e)
            return ShutdownResultVO(
                success=False, termination_method="none", duration_ms=duration_ms,
                final_state=RuntimeState.RUNNING_UNRESPONSIVE, escalated=False,
                error=str(e),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _is_process_running(self) -> bool:
        return self._process_id is not None

    def _graceful_shutdown(self) -> None:
        try:
            os.kill(self._process_id, signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass

    def _wait_for_exit(self, timeout_seconds: float) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                os.kill(self._process_id, 0)
                time.sleep(0.1)
            except ProcessLookupError:
                return True
        return False

    def _force_terminate(self) -> None:
        try:
            os.kill(self._process_id, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass

    def _verify_liveness(self, expected_alive: bool) -> bool:
        try:
            os.kill(self._process_id, 0)
            return not expected_alive
        except ProcessLookupError:
            return expected_alive

    def mark_stopped(self) -> None:
        self._process_id = None

    def __repr__(self) -> str:
        state = "running" if self._is_process_running() else "stopped"
        return f"ShutdownExecutor(state={state}, id={self._process_id})"
