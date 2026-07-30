"""CLI render command — Execute full frame render."""


from modules.shared.src.gateway.utility_socket_client import BlenderSocketClient

from .utility_cli_registry import Registry


def _mask_error(category: str, ref: str, message: str = "Operation failed") -> dict[str, object]:
    return {"success": False, "error": message, "category": category, "ref": ref}


def handle(args: object) -> dict[str, object]:
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
            result = client.send_command("render", params)
            return {"success": True, "message": "Render started", "filepath": args.output, "result": result}
    except ConnectionError:
        return _mask_error("connection", "cli-503", "Cannot connect to Blender — is it running?")
    except Exception:
        return _mask_error("unexpected", "cli-500")
