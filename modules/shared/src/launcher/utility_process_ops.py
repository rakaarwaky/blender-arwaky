"""Launcher utility: stateless OS process operations.

Provides pure functions for process liveness, signal sending, kill, spawn,
and readiness probing. No state, no side effects beyond OS calls.

Dependencies: Only taxonomy (for type annotations).
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import time

logger = logging.getLogger("BlenderMCPServer")


def process_alive(process_id: int) -> bool:
    """Check if a process is alive using os.kill(pid, 0).

    Returns False for invalid PIDs (<=0 or None).
    EPERM is logged but treated as alive (permission denied ≠ dead).
    """
    if process_id is None or process_id <= 0:
        return False
    try:
        os.kill(process_id, 0)
        return True
    except OSError as e:
        if e.errno == os.errno.ESRCH:
            return False
        logger.warning("os.kill(pid=%d) returned EPERM: %s", process_id, e)
        return False


def process_signal_term(process_id: int) -> bool:
    """Send SIGTERM to a process for graceful shutdown.

    Returns False for invalid PIDs. Logs warnings on failure.
    """
    if process_id is None or process_id <= 0:
        return False
    try:
        logger.debug("Sending SIGTERM to pid=%d", process_id)
        os.kill(process_id, signal.SIGTERM)
        return True
    except OSError as e:
        logger.warning("SIGTERM failed for pid=%d: %s", process_id, e)
        return False


def process_kill(process_id: int) -> bool:
    """Send SIGKILL to force-terminate a process.

    Returns False for invalid PIDs. Logs warnings on failure.
    """
    if process_id is None or process_id <= 0:
        return False
    try:
        logger.warning("Sending SIGKILL to pid=%d (escalated)", process_id)
        os.kill(process_id, signal.SIGKILL)
        return True
    except OSError as e:
        logger.error("SIGKILL failed for pid=%d: %s", process_id, e)
        return False


def process_spawn(
    executable: str,
    mode: str,
    bridge_endpoint: str | None = None,
    addon_path: str | None = None,
) -> int:
    """Spawn a Blender process with the given mode and optional integration args.

    FR-INT-002: Passes bridge endpoint and addon path as CLI arguments so the
    Gateway can connect to the running Blender instance.

    Returns the process PID. Mode 'headless' adds --background --python-exit-code 1.
    Uses a new process session (start_new_session=True) for orphan child cleanup support.
    """
    args = [executable]

    # FR-INT-002: Pass bridge endpoint and addon path for Gateway integration
    if bridge_endpoint:
        args += ["--bridge-endpoint", bridge_endpoint]
    if addon_path:
        args += ["--python-additional", addon_path]

    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]

    proc = subprocess.Popen(args, start_new_session=True)
    return proc.pid


def process_version_check(args: list[str], timeout: float = 5.0) -> tuple[int, str]:
    """Run a command and return (returncode, stdout)."""
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout


def process_probe_readiness(process_id: int, timeout_seconds: float, interval_seconds: float = 0.5) -> bool:
    """Poll process liveness until timeout. Returns True while alive.

    Checks at configurable interval (default 0.5s, per LauncherConfigVO.readiness_probe_interval_seconds);
    returns False if process dies before timeout.
    """
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not process_alive(process_id):
            return False
        time.sleep(interval_seconds)
    return True


def process_probe_bridge_readiness(process_id: int, timeout_seconds: float, bridge_endpoint: str | None = None) -> bool:
    """Poll process liveness AND bridge endpoint responsiveness.

    Returns True only when the process is alive AND the bridge health
    endpoint is reachable. Checks every 0.2 seconds.
    """
    if not bridge_endpoint:
        return process_probe_readiness(process_id, timeout_seconds)
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not process_alive(process_id):
            return False
        if _bridge_health_check(bridge_endpoint):
            return True
        time.sleep(0.2)
    return False


def _bridge_health_check(bridge_endpoint: str) -> bool:
    """Lightweight HTTP health check against the bridge endpoint."""
    import urllib.request

    try:
        req = urllib.request.Request(bridge_endpoint + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False
