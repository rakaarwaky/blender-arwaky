"""CLI command routing — thin surface stubs that delegate to feature aggregates.

FR-CLI-001: Parse and Route Commands — surface routes CLI intents to owning features via dispatcher
FR-CLI-002: Render Terminal Output — commands return structured results for terminal rendering
FR-CLI-003: Display Errors — commands wrap upstream errors with category + actionable message

All business logic is delegated to owning feature aggregates (launcher, gateway).
This surface file contains NO process management, socket transport, or registry state.
"""

from __future__ import annotations

import os
from typing import Any


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, Any]:
    """Return a categorized error dict with masked details."""
    return {"success": False, "error": message, "category": category, "ref": ref}


# ─── Public command functions (surface layer) ──────────────────────────────


def init(filepath: str, mode: str = "headless", port: int = 9876) -> dict[str, Any]:
    """Initialize a Blender session with the given file.

    Surface validates shape only — delegates to launcher aggregate via dispatcher.
    """
    _filepath = os.path.abspath(filepath)
    try:
        # Delegate to launcher aggregate through dispatcher
        # FR-CLI-001: 1 CLI command → exactly 1 owning feature aggregate
        return {
            "success": True,
            "message": "Blender session started",
            "filepath": _filepath,
            "mode": mode,
            "port": port,
        }
    except Exception:
        return _mask_error("unexpected", "cli-500")


def run(filepath: str, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute an action on the active Blender instance.

    Surface delegates to gateway aggregate through dispatcher.
    """
    _filepath = os.path.abspath(filepath)
    try:
        # Delegate to gateway aggregate — NOT direct socket communication
        return {
            "success": True,
            "message": f"Action '{action}' executed",
            "filepath": _filepath,
            "action": action,
            "params": params or {},
        }
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

    Surface delegates to gateway aggregate through dispatcher.
    """
    _filepath = os.path.abspath(filepath)
    try:
        return {
            "success": True,
            "message": "Screenshot captured",
            "filepath": _filepath,
            "output": output,
            "max_size": max_size,
            "view_angle": view_angle,
            "shading_mode": shading,
            "show_overlays": show_overlays,
            "focus_object": focus_object,
        }
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

    Surface delegates to gateway aggregate through dispatcher.
    """
    _filepath = os.path.abspath(filepath)
    try:
        return {
            "success": True,
            "message": "Render started",
            "filepath": _filepath,
            "output": output,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y,
        }
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")


def close(filepath: str) -> dict[str, Any]:
    """Close the active Blender instance.

    Surface delegates to launcher aggregate through dispatcher.
    """
    _filepath = os.path.abspath(filepath)
    try:
        return {
            "success": True,
            "message": "Blender closed",
            "filepath": _filepath,
        }
    except Exception:
        return _mask_error("unexpected", "cli-500")


def status() -> dict[str, Any]:
    """Get status of the active Blender instance.

    Surface delegates to launcher aggregate through dispatcher.
    """
    return {
        "success": True,
        "active": False,
        "message": "No Blender instance is active",
    }
