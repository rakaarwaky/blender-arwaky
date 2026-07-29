"""Shared action schemas — Config domain (used by CLI + MCP surfaces via dispatcher)."""

from typing import Any

CONFIG_ACTIONS: dict[str, dict[str, Any]] = {
    "get_config": {
        "description": "Retrieve BlenderArwaky configuration settings",
        "parameters": {
            "key": {"type": "string", "required": False, "description": "Specific config key to retrieve. Omit for all settings."},
        },
    },
    "set_config": {
        "description": "Update a configuration setting",
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Config key to update"},
            "value": {"type": "any", "required": True, "description": "New value for the config key"},
        },
    },
}
