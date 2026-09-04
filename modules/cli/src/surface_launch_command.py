"""CLI launch command — Start Blender session with a .blend file."""

from __future__ import annotations

import os

from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.cli.utility_cli_process import launch_blender


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object, _dispatcher: object | None = None) -> dict[str, object]:
    """Handle launch command: start Blender with the given file."""
    registry = Registry()

    error = registry.assert_no_active()
    if error:
        return _mask_error("state", "cli-409", error)

    raw_filepath = getattr(args, "filepath", None)
    if not raw_filepath:
        return _mask_error("validation_error", "cli-400", "--filepath is required for launch")

    filepath = os.path.abspath(str(raw_filepath))
    mode = getattr(args, "mode", "headless") or "headless"
    port = int(getattr(args, "port", 9876) or 9876)

    try:
        res = launch_blender(filepath, mode=mode, port=port)
        if not res.success or not res.data:
            return _mask_error(
                res.category or "launch_failed",
                res.ref or "cli-500",
                res.error or "Failed to launch Blender",
            )
        pid = int(res.data.get("pid", 0))
        registry.set_active(filepath, pid, port)
        return {
            "success": True,
            "message": res.message or f"Blender session launched for {filepath}",
            "filepath": filepath,
            "pid": pid,
            "port": port,
            "mode": mode,
        }
    except Exception:
        return _mask_error("unexpected", "cli-500")
