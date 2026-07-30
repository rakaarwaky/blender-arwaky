"""CLI init command — Start Blender with a file."""

import os

from modules.shared.src.cli.utility_cli_process import launch_blender
from modules.shared.src.cli.utility_cli_registry import Registry


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object) -> dict[str, object]:
    """Handle init command: start Blender with the given file."""
    registry = Registry()

    error = registry.assert_no_active()
    if error:
        return _mask_error("state", "cli-409", error)

    filepath = os.path.abspath(args.filepath)
    try:
        proc_info = launch_blender(filepath, mode=args.mode, port=args.port)
        registry.set_active(filepath, proc_info.pid, args.port)
        return {"success": True, "message": "Blender session started", "filepath": filepath, "pid": proc_info.pid, "port": args.port, "mode": args.mode}

    except Exception:
        return _mask_error("unexpected", "cli-500")
