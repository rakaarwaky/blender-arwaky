"""BlenderManager: Launches and manages Blender subprocess.

NOTE: This surface utility delegates process lifecycle to launcher feature (FR-LAU-001..004).
The CLI surface layer does not own business logic — it translates terminal input to aggregate calls.
"""

import os
import signal
import subprocess
import sys
import time


def find_blender() -> str:
    """Find Blender executable path."""
    # Check environment variable first
    env_path = os.environ.get("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path

    # Check common locations
    common_paths = [
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    # Try to find in PATH
    try:
        result = subprocess.run(
            ["which", "blender"],
            capture_output=True,
            text=True,
            timeout=5,
        )
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
    """Launch Blender with addon and return PID.

    Args:
        filepath: Path to .blend file
        mode: "gui" or "headless"
        port: TCP port for addon
        addon_path: Path to blender_mcp_addon directory

    Returns:
        PID of the Blender process
    """
    blender_exe = find_blender()

    # Build Blender command
    cmd = [blender_exe]

    if mode == "headless":
        cmd.append("--background")

    cmd.append(filepath)

    # Pre-save: if file doesn't exist, create it
    if not os.path.exists(filepath):
        # Create empty .blend file via Blender
        pre_save_script = f"""
import bpy
bpy.ops.wm.save_as_mainfile(filepath=r'{filepath}')
"""
        cmd.extend(["--python-expr", pre_save_script])

    # Inject addon
    if addon_path is None:
        # Default to blender_mcp_addon in project root
        project_root = os.path.join(os.path.dirname(__file__), "..", "..")
        addon_path = os.path.join(project_root, "blender_mcp_addon")

    if os.path.exists(addon_path):
        cmd.extend(
            [
                "--python-expr",
                f"""
import sys
sys.path.insert(0, r'{addon_path}')
import bpy
bpy.ops.preferences.addon_enable(module='blender_mcp_addon')
""",
            ]
        )

    # Launch process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL if mode == "headless" else None,
        stderr=subprocess.DEVNULL if mode == "headless" else None,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    # Wait for addon to start (poll port)
    _wait_for_addon(port, timeout=30)

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
    """Kill a Blender process by PID.

    Returns:
        True if killed successfully, False otherwise
    """
    try:
        if sys.platform == "win32":
            os.kill(pid, signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)
        # Wait briefly for graceful shutdown
        time.sleep(0.5)
        # Force kill if still alive
        try:
            os.kill(pid, 0)  # Check if alive
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass  # Already dead
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
