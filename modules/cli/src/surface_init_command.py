"""CLI init command — Start Blender with a file."""

import os
from typing import Any

from .utility_cli_process import launch_blender
from .utility_cli_registry import Registry


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, Any]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: Any) -> dict[str, Any]:
    """Handle init command: start Blender with the given file."""
    registry = Registry()

    error = registry.assert_no_active()
    if error:
        return _mask_error("state", "cli-409", error)

    filepath = os.path.abspath(args.filepath)
    try:
        pid = launch_blender(filepath, mode=args.mode, port=args.port)
        registry.set_active(filepath, pid, args.port)
        return {"success": True, "message": "Blender session started", "filepath": filepath, "pid": pid, "port": args.port, "mode": args.mode}
    except Exception:
        return _mask_error("unexpected", "cli-500")
