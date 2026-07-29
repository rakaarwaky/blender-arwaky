"""MCP render action schemas — parameter definitions and validation for viewport & render domain."""

from typing import Any

RENDER_ACTIONS: dict[str, dict[str, Any]] = {
    "get_viewport_screenshot": {
        "description": "Capture AI-optimized viewport screenshot",
        "parameters": {
            "filepath": {"type": "string", "required": False, "description": "Output path for screenshot"},
            "max_size": {"type": "integer", "required": False, "description": "Maximum dimension in pixels", "default": 800},
            "view_angle": {
                "type": "string",
                "required": False,
                "description": "Camera view angle",
                "enum": ["PERSPECTIVE", "TOP", "FRONT", "SIDE"],
                "default": "PERSPECTIVE",
            },
            "shading_mode": {
                "type": "string",
                "required": False,
                "description": "Viewport shading mode",
                "enum": ["WIREFRAME", "SOLID", "MATERIAL", "RENDERED"],
                "default": "MATERIAL",
            },
            "show_overlays": {"type": "boolean", "required": False, "description": "Show viewport overlays", "default": True},
            "focus_object": {"type": "string", "required": False, "description": "Object name to frame in viewport"},
        },
    },
    "render": {
        "description": "Execute a full frame render",
        "parameters": {
            "output_path": {"type": "string", "required": True, "description": "Output path for rendered image"},
            "resolution_x": {"type": "integer", "required": False, "description": "Render width in pixels", "default": 1920},
            "resolution_y": {"type": "integer", "required": False, "description": "Render height in pixels", "default": 1080},
        },
    },
}
