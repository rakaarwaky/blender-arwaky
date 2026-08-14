"""CLI render command — Execute full frame render."""

import os

from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object, _dispatcher: object | None = None) -> dict[str, object]:
    """Handle render command: execute full frame render."""
    registry = Registry()
    error = registry.assert_active(args.filepath)
    if error:
        return _mask_error("state", "cli-409", error)

    port = registry.get_port()
    params = {
        "output_path": args.output,
        "resolution_x": args.resolution_x,
        "resolution_y": args.resolution_y,
    }
    try:
        with BlenderSocketClient(port=port) as client:
            response = client.send_command("render", params)
            if response.get("status") != "success":
                return _mask_error("upstream", "cli-502", response.get("message", "Render failed"))
            if not os.path.exists(args.output):
                return _mask_error("unexpected", "cli-500", "Render file was not created")
            return {
                "success": True,
                "message": "Render completed",
                "filepath": args.output,
                "result": response.get("result"),
            }
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")
