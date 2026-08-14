"""Shared utility between CLI surface commands. Manages Blender lifecycle."""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import time


def find_blender() -> str:
    """Find Blender executable path."""
    env_path = os.environ.get("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path

    common_paths = [
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    try:
        result = subprocess.run(["which", "blender"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    raise FileNotFoundError("Blender not found. Set BLENDER_EXECUTABLE env var or install Blender.")


def launch_blender(
    filepath: str,
    mode: str = "headless",
    port: int = 9876,
    addon_path: str | None = None,
) -> int:
    """Launch Blender with addon and return PID."""
    blender_exe = find_blender()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    cmd = [blender_exe]
    if mode == "headless":
        cmd.append("--background")
    cmd.append(filepath)

    if not os.path.exists(filepath):
        pre_save_script = f"import bpy\nbpy.ops.wm.save_as_mainfile(filepath=r'{filepath}')"
        cmd.extend(["--python-expr", pre_save_script])

    if addon_path is None:
        addon_path = os.path.join(project_root, "blender_mcp_addon")

    if mode == "headless":
        headless_script = os.path.join(project_root, "scripts", "blender", "run_server_headless.py")
        cmd.extend(["--python", headless_script])
    elif os.path.exists(addon_path):
        cmd.extend(
            [
                "--python-expr",
                f"import sys\nsys.path.insert(0, r'{project_root}')\nimport bpy\nbpy.ops.preferences.addon_enable(module='blender_mcp_addon')",
            ]
        )

    try:
        process_env = os.environ.copy()
        process_env["BLENDERMCP_PORT"] = str(port)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL if mode == "headless" else None,
            stderr=subprocess.DEVNULL if mode == "headless" else None,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            env=process_env,
        )
    except OSError as e:
        raise RuntimeError(f"Failed to launch Blender process: {e}") from e

    try:
        _wait_for_addon(port, timeout=30)
    except TimeoutError as e:
        with contextlib.suppress(Exception):
            process.kill()
        raise RuntimeError(f"Blender addon not ready on port {port} after 30s") from e

    return process.pid


def _wait_for_addon(port: int, timeout: int = 30) -> None:
    """Wait for Blender addon to be ready on the port."""
    import socket

    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(("localhost", port))
            sock.close()
            return
        except (TimeoutError, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    raise TimeoutError(f"Blender addon not ready on port {port} after {timeout}s")


def kill_blender(pid: int) -> bool:
    """Kill a Blender process by PID."""
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        return True
    except OSError:
        return False


def is_running(pid: int) -> bool:
    """Check if a process is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
