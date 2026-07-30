"""Launcher utility: stateless OS process operations.

Provides pure functions for process liveness, signal sending, kill, spawn,
bridge readiness probing, and launch with bridge arguments. No state, no
side effects beyond OS calls.

Dependencies: Only taxonomy (for type annotations).
"""

from __future__ import annotations

import asyncio
import errno
import logging
import os
import signal
import socket
import time

from .taxonomy_launcher_vo import RuntimeStateVO

_taxonomy_types = (RuntimeStateVO,)

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


async def _async_spawn(cmd: list[str]) -> asyncio.subprocess.Process:
    return await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )


def process_spawn(
    executable: str,
    mode: str,
    bridge_host: str = "localhost",
    bridge_port: int = 9876,
    protocol_version: str = "2.0.0",
) -> int:
    """Spawn a Blender process with the given mode and activate the bridge.

    FR-LAU-002 / P1: Provides bridge endpoint + protocol information to enable

    the integration component (addon/bridge) to start listening.

    Returns the process PID. Mode 'headless' adds --background --python-exit-code 1.
    """
    args = [executable]
    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]

    args += [
        "--python",
        "bridge_startup_script.py",
        "--",
        f"--bridge-host={bridge_host}",
        f"--bridge-port={bridge_port}",
        f"--protocol-version={protocol_version}",
    ]

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        proc = loop.run_until_complete(_async_spawn(args))
    else:
        proc = asyncio.run(_async_spawn(args))
    return proc.pid


async def _async_run(cmd: list[str]) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()
    return proc.returncode or 0, stdout.decode()


def process_version_check(args: list[str], timeout: float = 5.0) -> tuple[int, str]:
    """Run a command and return (returncode, stdout)."""
    _ = timeout
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return loop.run_until_complete(_async_run(args))
    return asyncio.run(_async_run(args))


def process_probe_readiness(
    process_id: int,
    bridge_host: str = "localhost",
    bridge_port: int = 9876,
    timeout_seconds: float = 30.0,
) -> bool:
    """Poll process liveness AND bridge readiness until timeout."""
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if not process_alive(process_id):
            return False

        if bridge_is_responsive(bridge_host, bridge_port, timeout_seconds=0.5):
            return True

        time.sleep(0.2)

    return False


def bridge_is_responsive(host: str, port: int, timeout_seconds: float = 0.5) -> bool:
    """Check if a bridge is responsive via TCP connect."""
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False
