"""CLI process helpers — launch, find, kill, check Blender process."""

from __future__ import annotations

import contextlib
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import time

from modules.shared.src.cli.taxonomy_cli_vo import BlenderProcessVo, CliResultVo


def find_blender() -> CliResultVo:
    """Find Blender executable path returning CliResultVo VO."""
    env_path = os.environ.get("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return CliResultVo(success=True, message=env_path, data={"executable_path": env_path})

    common_paths = [
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return CliResultVo(success=True, message=path, data={"executable_path": path})

    found = shutil.which("blender")
    if found and os.path.exists(found):
        return CliResultVo(success=True, message=found, data={"executable_path": found})

    return CliResultVo(
        success=False,
        error="Blender not found. Set BLENDER_EXECUTABLE env var or install Blender.",
        category="not_found",
        ref="cli-404",
    )


def launch_blender(
    filepath: str,
    mode: str = "headless",
    port: int = 9876,
    addon_path: str | None = None,
) -> CliResultVo:
    """Launch Blender with addon returning CliResultVo VO."""
    blender_res = find_blender()
    if not blender_res.success or not blender_res.message:
        return blender_res

    blender_exe = blender_res.message
    pathlib.Path(filepath)
    cmd = [blender_exe]
    if mode == "headless":
        cmd.append("--background")
    cmd.append(filepath)

    if not os.path.exists(filepath):
        pre_save_script = f"import bpy\nbpy.ops.wm.save_as_mainfile(filepath=r'{filepath}')"
        cmd.extend(["--python-expr", pre_save_script])

    if addon_path is None:
        project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        addon_path = os.path.join(project_root, "blender_mcp_addon")

    if os.path.exists(addon_path):
        cmd.extend(
            [
                "--python-expr",
                f"import sys\nsys.path.insert(0, r'{addon_path}')\nimport bpy\nbpy.ops.preferences.addon_enable(module='blender_mcp_addon')",
            ]
        )

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL if mode == "headless" else None,
            stderr=subprocess.DEVNULL if mode == "headless" else None,
            shell=False,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
    except OSError as e:
        return CliResultVo(
            success=False,
            error=f"Failed to launch Blender process: {e}",
            category="launch_failed",
            ref="cli-500",
        )

    try:
        _wait_for_addon(port, timeout=30)
    except TimeoutError as e:
        with contextlib.suppress(Exception):
            process.kill()
        return CliResultVo(
            success=False,
            error=f"Blender addon not ready on port {port} after 30s: {e}",
            category="timeout",
            ref="cli-504",
        )

    proc_vo = BlenderProcessVo(pid=process.pid, port=port, filepath=filepath, is_running=True)
    return CliResultVo(
        success=True,
        message="Blender session started",
        data={"process": proc_vo, "pid": process.pid, "port": port},
    )


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


def kill_blender(pid: int) -> CliResultVo:
    """Kill a Blender process by PID returning CliResultVo VO."""
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            ...  # Process already terminated
        return CliResultVo(success=True, message=f"Process {pid} terminated")
    except OSError as e:
        return CliResultVo(
            success=False,
            error=f"Failed to kill process {pid}: {e}",
            category="process_error",
            ref="cli-400",
        )


def is_running(pid: int) -> CliResultVo:
    """Check if a process is running returning CliResultVo VO."""
    try:
        os.kill(pid, 0)
        return CliResultVo(success=True, message="Process is running", data={"is_running": True})
    except OSError:
        return CliResultVo(success=False, message="Process is not running", data={"is_running": False})
