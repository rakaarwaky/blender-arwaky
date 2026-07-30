"""CLI screenshot command — Capture viewport screenshot."""

import os

from modules.shared.src.cli.utility_cli_registry import Registry
from modules.shared.src.gateway.utility_socket_client import BlenderSocketClient


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object) -> dict[str, object]:
    """Handle screenshot command: capture viewport screenshot."""
    registry = Registry()
    error = registry.assert_active(args.filepath)
    if error:
        return _mask_error("state", "cli-409", error)

    port = registry.get_port()
    params = {
        "filepath": args.output,
        "max_size": args.max_size,
        "view_angle": args.view_angle,
        "shading_mode": args.shading,
        "show_overlays": not args.no_overlays,
        "focus_object": args.focus_object,
    }

    try:
        with BlenderSocketClient(port=port) as client:
            result = client.send_command("get_viewport_screenshot", params)
            if os.path.exists(args.output):
                return {"success": True, "message": "Screenshot saved", "filepath": args.output, "result": result}
            return _mask_error("unexpected", "cli-500", "Screenshot file was not created")
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")
