"""MCP scene action schemas — parameter definitions and validation for scene domain actions."""

from typing import Any

SCENE_ACTIONS: dict[str, dict[str, Any]] = {
    "get_scene_info": {
        "description": "Full scene metadata — object count, frame range, resolution, render engine",
        "parameters": {},
    },
    "cleanup_scene": {
        "description": "Remove objects from scene by mode",
        "parameters": {
            "mode": {
                "type": "string",
                "required": True,
                "description": "Cleanup scope",
                "enum": ["all", "objects", "meshes"],
            },
        },
    },
    "setup_environment": {
        "description": "Setup HDRI lighting for the scene",
        "parameters": {
            "hdri_id": {"type": "string", "required": True, "description": "HDRI asset identifier"},
            "strength": {"type": "number", "required": False, "description": "Light intensity multiplier", "default": 1.0},
        },
    },
}
