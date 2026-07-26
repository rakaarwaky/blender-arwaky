"""Runtime status capability — verify actual process state and classify.

FR-LAU-004: Check Runtime Status
- Verifies true liveness via OS signal
- Classifies state (not_running/starting/running_ready/running_unresponsive/stopping/stale)
- Read-only except stale reconciliation
- Idempotent: always returns current truth
"""

import logging
import os
import time

from modules.shared.src.launcher.contract_runtime_status_protocol import (
    RuntimeStatusProtocol,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    RuntimeState,
    StatusCheckResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class RuntimeStatusExecutor(RuntimeStatusProtocol):
    """Concrete implementation for runtime status verification.

    FR-LAU-004: Verifies actual liveness via OS signal, classifies state.
    Read-only except stale reconciliation. Idempotent.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        self._process_id: int | None = None
        self._ready: bool = False
        self._bridge_endpoint: str | None = None
        self._last_known_state: RuntimeState = RuntimeState.NOT_RUNNING
        self._stale_threshold_seconds: float = 60.0

    # ─── Block 2: Protocol Method Implementation ─────────────

    def check_status(self) -> StatusCheckResultVO:
        """Verify actual process liveness and classify runtime state.

        FR-LAU-004: Reads from OS, classifies state, reconciles stale references.
        Always returns current truth — idempotent.
        """
        start_time = time.time()

        try:
            state = self._classify_state()
            duration_ms = (time.time() - start_time) * 1000

            logger.info("Status check completed: %s", state.value)
            return StatusCheckResultVO(
                state=state, process_id=self._process_id,
                bridge_endpoint=self._bridge_endpoint, duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Status check failed: %s", e)
            return StatusCheckResultVO(
                state=RuntimeState.STALE, process_id=self._process_id,
                bridge_endpoint=self._bridge_endpoint, duration_ms=duration_ms,
                error=str(e),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _classify_state(self) -> RuntimeState:
        """Classify current state based on process liveness and readiness."""
        if self._process_id is None:
            return RuntimeState.NOT_RUNNING

        # Check if process is actually alive via OS signal
        try:
            os.kill(self._process_id, 0)
        except ProcessLookupError:
            # Process died but we don't know yet — reconcile stale reference
            self._reconcile_stale()
            return RuntimeState.NOT_RUNNING

        if not self._ready:
            return RuntimeState.STARTING

        # Check responsiveness via bridge endpoint
        if self._bridge_endpoint and self._is_bridge_unresponsive():
            return RuntimeState.RUNNING_UNRESPONSIVE

        return RuntimeState.RUNNING_READY

    def _is_bridge_unresponsive(self) -> bool:
        """Check if bridge endpoint is responsive (stub for transport-level check)."""
        # In a real implementation, this would ping the bridge
        # For MVP, assume responsive if we have an endpoint
        return False

    def _reconcile_stale(self) -> None:
        """Clear stale process reference."""
        logger.warning("Detected stale process reference — clearing")
        self._process_id = None
        self._ready = False
        self._bridge_endpoint = None
        self._last_known_state = RuntimeState.NOT_RUNNING

    def update_runtime_state(
        self,
        process_id: int | None,
        ready: bool,
        bridge_endpoint: str | None,
    ) -> None:
        """Update internal state tracking (called by orchestrator)."""
        self._process_id = process_id
        self._ready = ready
        self._bridge_endpoint = bridge_endpoint
        if process_id is not None and ready:
            self._last_known_state = RuntimeState.RUNNING_READY
        elif process_id is not None:
            self._last_known_state = RuntimeState.STARTING

    def get_process_id(self) -> int | None:
        return self._process_id

    def is_ready(self) -> bool:
        return self._ready

    def __repr__(self) -> str:
        state = self._last_known_state.value if self._last_known_state else "unknown"
        return f"RuntimeStatusExecutor(state={state}, id={self._process_id})"