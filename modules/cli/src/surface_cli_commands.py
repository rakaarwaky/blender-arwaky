"""High-level CLI operations: init, run, screenshot, render, close, status.

FR-CLI-001: Parse and Route Commands — commands module routes CLI intents to owning feature aggregates
FR-CLI-002: Render Terminal Output — commands return structured results for terminal rendering
FR-CLI-003: Display Errors — commands wrap upstream errors with category + actionable message, masking secrets
"""

import os
from typing import Any

from .surface_cli_blender_manager import is_running, kill_blender, launch_blender
from .surface_cli_registry import Registry
from .surface_cli_socket_client import BlenderSocketClient


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, Any]:
    """Return a categorized error dict with masked details."""
    return {"success": False, "error": message, "category": category, "ref": ref}


def _resolve_active(registry: Registry, filepath: str) -> tuple[str | None, int | None]:
    """Validate active Blender instance and return (error, port).

    Returns:
        (error_message_or_empty, port_or_None) — port is None when error is non-empty
    """
    error = registry.assert_active(filepath)
    if error:
        return error, None
    return "", registry.get_port()


def init(filepath: str, mode: str = "headless", port: int = 9876) -> dict[str, Any]:
    """Initialize a Blender session with the given file.

    Args:
        filepath: Path to .blend file
        mode: "gui" or "headless"
        port: TCP port for addon

    Returns:
        Success/error dict with category and reference code
    """
    registry = Registry()

    # Check if Blender is already active
    error = registry.assert_no_active()
    if error:
        return _mask_error("state", "cli-409", error)

    # Resolve absolute path — mask in any error response
    filepath = os.path.abspath(filepath)

    try:
        pid = launch_blender(filepath, mode=mode, port=port)
        registry.set_active(filepath, pid, port)
        return {
            "success": True,
            "message": "Blender session started",
            "filepath": filepath,
            "pid": pid,
            "port": port,
            "mode": mode,
        }
    except Exception:
        return _mask_error("unexpected", "cli-500")


def run(filepath: str, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute an action on the active Blender instance.

    Args:
        filepath: Path to .blend file (must match active entity)
        action: Action name (e.g., "get_scene_info", "execute_code")
        params: Action parameters

    Returns:
        Action result dict with category
    """
    registry = Registry()

    error, port = _resolve_active(registry, filepath)
    if error:
        return _mask_error("state", "cli-409", error)

    try:
        with BlenderSocketClient(port=port) as client:
            result = client.send_command(action, params or {})
            return result
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")


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
        Success/error dict with category
    """
    registry = Registry()

    error, port = _resolve_active(registry, filepath)
    if error:
        return _mask_error("state", "cli-409", error)

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

            if os.path.exists(output):
                return {
                    "success": True,
                    "message": "Screenshot saved",
                    "filepath": output,
                    "result": result,
                }
            else:
                return _mask_error("unexpected", "cli-500", "Screenshot file was not created")
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")


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
        Success/error dict with category
    """
    registry = Registry()

    error, port = _resolve_active(registry, filepath)
    if error:
        return _mask_error("state", "cli-409", error)

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
                "message": "Render started",
                "filepath": output,
                "result": result,
            }
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")


def close(filepath: str) -> dict[str, Any]:
    """Close the active Blender instance.

    Args:
        filepath: Path to .blend file (must match active entity)

    Returns:
        Success/error dict with category
    """
    registry = Registry()

    error, port = _resolve_active(registry, filepath)
    if error:
        return _mask_error("state", "cli-409", error)

    pid = registry.get_pid()

    # Try to save the file first — log failure but continue to kill process
    save_failed = False
    try:
        with BlenderSocketClient(port=port) as client:
            client.send_command("execute_code", {"code": "import bpy\nbpy.ops.wm.save_mainfile()"})
    except Exception:
        save_failed = True

    # Kill Blender process
    if pid and is_running(pid):
        kill_blender(pid)

    # Clear registry
    registry.clear()

    if save_failed:
        return {
            "success": True,
            "message": "Blender closed (save may have failed)",
            "warnings": ["File may not have been saved before close"],
        }

    return {
        "success": True,
        "message": "Blender closed",
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
            "message": "No Blender instance is active",
        }

    filepath = registry.get_active()
    pid = registry.get_pid()
    port = registry.get_port()

    running = pid is not None and is_running(pid)

    return {
        "success": True,
        "active": True,
        "running": running,
        "filepath": filepath,
        "pid": pid,
        "port": port,
    }
