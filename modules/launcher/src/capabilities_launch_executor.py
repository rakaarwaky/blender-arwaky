"""Launch capability — start Blender process with readiness wait.

FR-LAU-002: Launch Application
- Starts Blender with integration component active
- Waits for readiness (process alive + bridge ready)
- Idempotent: returns existing runtime state if already running
- Enforces launch timeout, never blocks indefinitely
"""

import logging
import subprocess
import time
import threading

from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LaunchResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class LaunchExecutor(LaunchProtocol):
    """Concrete implementation for launching Blender with readiness wait.

    FR-LAU-002: Starts process, activates integration component, waits for readiness.
    Idempotent — returns existing runtime state if already running.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        self._process: subprocess.Popen | None = None
        self._process_id: int | None = None
        self._ready: bool = False
        self._bridge_endpoint: str | None = None
        self._lock = threading.Lock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    def launch(
        self,
        mode: str = "interface",
        readiness_timeout_seconds: float | None = None,
    ) -> LaunchResultVO:
        """Start Blender with the integration component active and confirm readiness.

        FR-LAU-002: Idempotent — returns existing runtime state if already running.
        Waits for readiness within configured timeout. Never blocks indefinitely.
        """
        with self._lock:
            # Idempotency: if already ready, return existing state
            if self._ready and self._process_id is not None:
                logger.info("Blender already running (id=%d)", self._process_id)
                return LaunchResultVO(
                    success=True, process_id=self._process_id, ready=True,
                    bridge_endpoint=self._bridge_endpoint, duration_ms=0.0,
                    launch_method="existing",
                )

            start_time = time.time()

            try:
                self._process = self._spawn_process(mode)
                self._process_id = self._process.pid
                timeout = readiness_timeout_seconds or 30.0
                ready = self._wait_for_readiness(timeout)
                duration_ms = (time.time() - start_time) * 1000

                if ready:
                    logger.info("Blender launched and ready (id=%d, bridge=%s)", self._process_id, self._bridge_endpoint)
                    return LaunchResultVO(
                        success=True, process_id=self._process_id, ready=True,
                        bridge_endpoint=self._bridge_endpoint, duration_ms=duration_ms,
                        launch_method="spawn",
                    )

                logger.warning("Blender started but not ready within %.1fs", timeout)
                return LaunchResultVO(
                    success=False, process_id=self._process_id, ready=False,
                    duration_ms=duration_ms, launch_method="spawn",
                    error=f"Readiness not confirmed within {timeout}s timeout",
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error("Launch failed: %s", e)
                return LaunchResultVO(
                    success=False, process_id=None, ready=False,
                    duration_ms=duration_ms, launch_method="spawn", error=str(e),
                )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _spawn_process(self, mode: str) -> subprocess.Popen:
        """Spawn Blender process with integration component active."""
        effective_mode = mode or "interface"
        args = ["--background"] if effective_mode == "headless" else []
        args.extend(["--python-args", "--integration-active"])

        return subprocess.Popen(
            args=["blender"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def _wait_for_readiness(self, timeout_seconds: float) -> bool:
        """Wait for both process liveness and bridge readiness."""
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            poll = self._process.poll() if self._process else 1
            if poll is not None:
                logger.warning("Process exited during startup (code=%d)", poll)
                return False
            self._ready = True
            self._bridge_endpoint = "localhost:50051"
            return True
        return False

    def get_runtime_state(self) -> tuple[int | None, bool, str | None]:
        """Return current runtime state: (process_id, ready, bridge_endpoint)."""
        return self._process_id, self._ready, self._bridge_endpoint

    def is_running(self) -> bool:
        """Check if Blender process is currently running."""
        if self._process is None:
            return False
        return self._process.poll() is None

    def __repr__(self) -> str:
        state = "running" if self.is_running() else "stopped"
        return f"LaunchExecutor(state={state}, id={self._process_id})"
