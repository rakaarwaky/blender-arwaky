"""Commands: High-level CLI operations (init, run, screenshot, render, close, status)."""

import os
from typing import Any

from .blender_manager import is_running, kill_blender, launch_blender
from .registry import Registry
from .socket_client import BlenderSocketClient


def init(filepath: str, mode: str = "headless", port: int = 9876) -> dict[str, Any]:
    """Initialize a Blender session with the given file.

    Args:
        filepath: Path to .blend file
        mode: "gui" or "headless"
        port: TCP port for addon

    Returns:
        Success/error dict
    """
    registry = Registry()

    # Check if Blender is already active
    error = registry.assert_no_active()
    if error:
        return {"success": False, "error": error}

    # Resolve absolute path
    filepath = os.path.abspath(filepath)

    try:
        # Launch Blender
        pid = launch_blender(filepath, mode=mode, port=port)

        # Register in registry
        registry.set_active(filepath, pid, port)

        return {
            "success": True,
            "message": f"Blender started for '{os.path.basename(filepath)}'",
            "filepath": filepath,
            "pid": pid,
            "port": port,
            "mode": mode,
        }
    except Exception as e:
        return {"success": False, "error": f"Gagal memulai Blender: {e}"}


def run(filepath: str, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute an action on the active Blender instance.

    Args:
        filepath: Path to .blend file (must match active entity)
        action: Action name (e.g., "get_scene_info", "execute_code")
        params: Action parameters

    Returns:
        Action result dict
    """
    registry = Registry()

    # Validate entity is active
    error = registry.assert_active(filepath)
    if error:
        return {"success": False, "error": error}

    port = registry.get_port()

    try:
        with BlenderSocketClient(port=port) as client:
            result = client.send_command(action, params or {})
            return result
    except Exception as e:
        return {"success": False, "error": f"Command '{action}' failed: {e}"}


def screenshot(
    filepath: str,
    output: str,
    max_size: int = 800,
    view_angle: str = "PERSPECTIVE",
    shading: str = "MATERIAL",
    show_overlays: bool = True,
    focus_object: str | None = None,
) -> dict[str, Any]:
    """Capture a viewport screenshot.

    Args:
        filepath: Path to .blend file (must match active entity)
        output: Output path for the screenshot image
        max_size: Maximum dimension in pixels
        view_angle: PERSPECTIVE, TOP, FRONT, or SIDE
        shading: WIREFRAME, SOLID, MATERIAL, or RENDERED
        show_overlays: Show viewport overlays
        focus_object: Object name to frame

    Returns:
        Success/error dict with filepath
    """
    registry = Registry()

    # Validate entity is active
    error = registry.assert_active(filepath)
    if error:
        return {"success": False, "error": error}

    port = registry.get_port()

    params = {
        "filepath": output,
        "max_size": max_size,
        "view_angle": view_angle,
        "shading_mode": shading,
        "show_overlays": show_overlays,
        "focus_object": focus_object,
    }

    try:
        with BlenderSocketClient(port=port) as client:
            result = client.send_command("get_viewport_screenshot", params)

            # Check if file was created
            if os.path.exists(output):
                return {
                    "success": True,
                    "message": f"Screenshot saved to '{output}'",
                    "filepath": output,
                    "result": result,
                }
            else:
                return {"success": False, "error": "Screenshot file was not created"}
    except Exception as e:
        return {"success": False, "error": f"Screenshot failed: {e}"}


def render(
    filepath: str,
    output: str,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
) -> dict[str, Any]:
    """Execute a full frame render.

    Args:
        filepath: Path to .blend file (must match active entity)
        output: Output path for the rendered image
        resolution_x: Render width in pixels
        resolution_y: Render height in pixels

    Returns:
        Success/error dict with filepath
    """
    registry = Registry()

    # Validate entity is active
    error = registry.assert_active(filepath)
    if error:
        return {"success": False, "error": error}

    port = registry.get_port()

    params = {
        "output_path": output,
        "resolution_x": resolution_x,
        "resolution_y": resolution_y,
    }

    try:
        with BlenderSocketClient(port=port) as client:
            result = client.send_command("render", params)

            return {
                "success": True,
                "message": f"Render saved to '{output}'",
                "filepath": output,
                "result": result,
            }
    except Exception as e:
        return {"success": False, "error": f"Render failed: {e}"}


def close(filepath: str) -> dict[str, Any]:
    """Close the active Blender instance.

    Args:
        filepath: Path to .blend file (must match active entity)

    Returns:
        Success/error dict
    """
    registry = Registry()

    # Validate entity is active
    error = registry.assert_active(filepath)
    if error:
        return {"success": False, "error": error}

    pid = registry.get_pid()
    port = registry.get_port()

    # Try to save the file first
    try:
        with BlenderSocketClient(port=port) as client:
            client.send_command("execute_code", {"code": "import bpy\nbpy.ops.wm.save_mainfile()"})
    except Exception:
        pass  # Best effort save

    # Kill Blender process
    if pid and is_running(pid):
        kill_blender(pid)

    # Clear registry
    registry.clear()

    return {
        "success": True,
        "message": f"Blender closed for '{os.path.basename(filepath)}'",
    }


def status() -> dict[str, Any]:
    """Get status of the active Blender instance.

    Returns:
        Status dict with active entity info
    """
    registry = Registry()

    if not registry.is_active():
        return {
            "success": True,
            "active": False,
            "message": "Tidak ada Blender yang aktif",
        }

    filepath = registry.get_active()
    pid = registry.get_pid()
    port = registry.get_port()

    # Check if process is still running
    running = pid is not None and is_running(pid)

    return {
        "success": True,
        "active": True,
        "running": running,
        "filepath": filepath,
        "pid": pid,
        "port": port,
    }
