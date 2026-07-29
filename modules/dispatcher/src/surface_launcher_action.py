"""Shared action schemas — Launcher domain (used by CLI + MCP surfaces via dispatcher)."""

from typing import Any

LAUNCHER_ACTIONS: dict[str, dict[str, Any]] = {
    "launch_blender": {
        "description": "Start Blender with integration component active",
        "parameters": {
            "mode": {
                "type": "string",
                "required": False,
                "description": "Blender launch mode",
                "enum": ["interface", "headless"],
                "default": "headless",
            },
            "port": {"type": "integer", "required": False, "description": "TCP port for addon communication", "default": 9876},
        },
    },
    "shutdown_blender": {
        "description": "Gracefully shut down Blender with force termination fallback",
        "parameters": {
            "force": {"type": "boolean", "required": False, "description": "Skip graceful shutdown and force terminate", "default": False},
        },
    },
    "get_runtime_status": {
        "description": "Verify true Blender process liveness and readiness",
        "parameters": {},
    },
    "register_executable": {
        "description": "Locate and register the Blender executable path",
        "parameters": {
            "path": {"type": "string", "required": False, "description": "Explicit path to Blender executable"},
        },
    },
}
