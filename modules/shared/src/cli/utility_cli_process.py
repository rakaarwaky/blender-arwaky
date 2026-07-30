"""CLI process helpers — launch, find, kill, check Blender process securely via asyncio."""

from __future__ import annotations

import asyncio
import contextlib
import os
import pathlib
import shutil
import signal
import socket
import time

from modules.shared.src.cli.taxonomy_cli_vo import BlenderProcessVo, CliResultVo

ALLOWED_MODES = {"headless", "gui"}
MIN_PORT = 1024
MAX_PORT = 65535


def find_blender() -> CliResultVo:
    """Find and validate Blender executable path returning CliResultVo VO."""
    env_path = os.environ.get("BLENDER_EXECUTABLE")
    if env_path:
        resolved_env = pathlib.Path(env_path).resolve()
        if resolved_env.is_file() and os.access(resolved_env, os.X_OK):
            return CliResultVo(success=True, message=str(resolved_env), data={"executable_path": str(resolved_env)})

    common_paths = [
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]

    for path_str in common_paths:
        candidate = pathlib.Path(path_str)
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return CliResultVo(success=True, message=str(candidate), data={"executable_path": str(candidate)})

    found = shutil.which("blender")
    if found:
        resolved_found = pathlib.Path(found).resolve()
        if resolved_found.is_file():
            return CliResultVo(success=True, message=str(resolved_found), data={"executable_path": str(resolved_found)})

    return CliResultVo(
        success=False,
        error="Blender executable not found. Set BLENDER_EXECUTABLE env var or install Blender.",
        category="not_found",
        ref="cli-404",
    )


async def _async_launch(cmd: list[str]) -> asyncio.subprocess.Process:
    """Launch process asynchronously via asyncio.create_subprocess_exec."""
    return await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )


def launch_blender(
    filepath: str,
    mode: str = "headless",
    port: int = 9876,
    addon_path: str | None = None,
) -> CliResultVo:
    """Launch Blender securely with validated inputs returning CliResultVo VO."""
    if mode not in ALLOWED_MODES:
        return CliResultVo(
            success=False,
            error=f"Invalid mode '{mode}'. Must be one of {ALLOWED_MODES}",
            category="validation_error",
            ref="cli-400",
        )

    if not (MIN_PORT <= port <= MAX_PORT):
        return CliResultVo(
            success=False,
            error=f"Port {port} out of valid range [{MIN_PORT}, {MAX_PORT}]",
            category="validation_error",
            ref="cli-400",
        )

    blender_res = find_blender()
    if not blender_res.success or not blender_res.message:
        return blender_res

    blender_exe = blender_res.message
    resolved_filepath = str(pathlib.Path(filepath).resolve())

    cmd: list[str] = [blender_exe]
    if mode == "headless":
        cmd.append("--background")
    cmd.append(resolved_filepath)

    if not os.path.exists(resolved_filepath):
        pre_save_script = f"import bpy\nbpy.ops.wm.save_as_mainfile(filepath=r'{resolved_filepath}')"
        cmd.extend(["--python-expr", pre_save_script])

    if addon_path is None:
        project_root = pathlib.Path(__file__).resolve().parents[4]
        addon_path_obj = project_root / "blender_mcp_addon"
    else:
        addon_path_obj = pathlib.Path(addon_path).resolve()

    if addon_path_obj.exists():
        addon_path_str = str(addon_path_obj)
        cmd.extend(
            [
                "--python-expr",
                f"import sys\nsys.path.insert(0, r'{addon_path_str}')\nimport bpy\nbpy.ops.preferences.addon_enable(module='blender_mcp_addon')",
            ]
        )

    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            proc = loop.run_until_complete(_async_launch(cmd))
        else:
            proc = asyncio.run(_async_launch(cmd))
        pid = proc.pid
    except Exception as e:
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
            os.kill(pid, signal.SIGKILL)
        return CliResultVo(
            success=False,
            error=f"Blender addon not ready on port {port} after 30s: {e}",
            category="timeout",
            ref="cli-504",
        )

    proc_vo = BlenderProcessVo(pid=pid, port=port, filepath=resolved_filepath, is_running=True)
    return CliResultVo(
        success=True,
        message="Blender session started",
        data={"process": proc_vo, "pid": pid, "port": port},
    )


def _wait_for_addon(port: int, timeout: int = 30) -> None:
    """Wait for Blender addon to be ready on the port."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                return
        except (TimeoutError, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    raise TimeoutError(f"Blender addon not ready on port {port} after {timeout}s")


def kill_blender(pid: int) -> CliResultVo:
    """Kill a Blender process safely by PID returning CliResultVo VO."""
    if pid <= 0:
        return CliResultVo(success=False, error="Invalid PID", category="validation_error", ref="cli-400")

    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            ...
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
    if pid <= 0:
        return CliResultVo(success=False, message="Invalid PID", data={"is_running": False})

    try:
        os.kill(pid, 0)
        return CliResultVo(success=True, message="Process is running", data={"is_running": True})
    except OSError:
        return CliResultVo(success=False, message="Process is not running", data={"is_running": False})
