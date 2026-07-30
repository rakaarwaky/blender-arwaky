"""Launcher utility: stateless OS process operations.

Provides pure functions for process liveness, signal sending, kill, spawn,
bridge readiness probing, and launch with bridge arguments. No state, no
side effects beyond OS calls.

Dependencies: Only taxonomy (for type annotations).
"""

from __future__ import annotations

import errno
import logging
import os
import signal
import socket
import subprocess
import time

logger = logging.getLogger("BlenderMCPServer")


def process_alive(process_id: int | None) -> bool:
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
        if e.errno == errno.ESRCH:
            return False
        logger.warning("os.kill(pid=%d) returned EPERM: %s", process_id, e)
        return True


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
    bridge_host: str = "localhost",
    bridge_port: int = 9876,
    protocol_version: str = "2.0.0",
) -> int:
    """Spawn a Blender process with the given mode and activate the bridge.

    FR-LAU-002 / P1: Passes bridge endpoint + protocol information to enable
    the integration component (addon/bridge) to start listening.

    Returns the process PID. Mode 'headless' adds --background --python-exit-code 1.
    """
    args = [executable]
    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]

    # Activate the integration component and pass bridge settings
    args += [
        "--python",
        "bridge_startup_script.py",
        "--",
        f"--bridge-host={bridge_host}",
        f"--bridge-port={bridge_port}",
        f"--protocol-version={protocol_version}",
    ]

    proc = subprocess.Popen(args)
    return proc.pid


def process_version_check(args: list[str], timeout: float = 5.0) -> tuple[int, str]:
    """Run a command and return (returncode, stdout)."""
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout


def process_probe_readiness(
    process_id: int,
    bridge_host: str = "localhost",
    bridge_port: int = 9876,
    timeout_seconds: float = 30.0,
) -> bool:
    """Poll process liveness AND bridge readiness until timeout.

    FR-LAU-004 / P1: Full-depth readiness requires BOTH process liveness
    AND bridge responsiveness (TCP connect + bridge status/ping).

    Returns True only when both checks pass; returns False if process dies
    or bridge does not respond within timeout.
    """
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        # Check process liveness first
        if not process_alive(process_id):
            return False

        # Check bridge responsiveness (TCP connect)
        if bridge_is_responsive(bridge_host, bridge_port, timeout_seconds=0.5):
            return True

        time.sleep(0.2)

    return False


def bridge_is_responsive(host: str, port: int, timeout_seconds: float = 0.5) -> bool:
    """Check if a bridge is responsive via TCP connect.

    P1: Used by process_probe_readiness to verify bridge component is active.
    Returns True if a TCP connection can be established within timeout.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False
