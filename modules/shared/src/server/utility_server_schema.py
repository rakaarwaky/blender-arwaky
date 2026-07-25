"""Utility: Command argument schema validation for Blender commands.

Stateless standalone functions that validate command arguments
against defined schemas before sending to Blender.
Domain-agnostic — reusable across modules.
"""

from __future__ import annotations

from typing import Any

from ..common.taxonomy_domain_error import ValidationError


# Command argument schemas per FR-SRV-003
_COMMAND_SCHEMAS: dict[str, list[str]] = {
    "get_scene_info": [],
    "get_object_info": ["name"],
    "get_screenshot": ["max_size", "view_angle", "shading_mode", "show_overlays", "focus_object"],
    "execute_code": ["code"],
}


def validate_command_args(command: str, params: dict[str, Any] | None) -> None:
    """Validate command arguments against defined schema.

    Raises ValidationError if:
    - Command is unknown
    - Params contain keys not in schema
    - Required parameters are missing

    Args:
        command: The command/action name to validate.
        params: Command arguments dictionary.

    Raises:
        ValidationError: If command or arguments are invalid.
    """
    if command not in _COMMAND_SCHEMAS:
        raise ValidationError(f"Unknown command: {command}")

    allowed_keys = set(_COMMAND_SCHEMAS[command])

    if params is None:
        return

    if not isinstance(params, dict):
        raise ValidationError("Command arguments must be a dictionary")

    # Check for unknown keys
    for key in params:
        if key not in allowed_keys:
            raise ValidationError(f"Unknown parameter '{key}' for command '{command}'")


def get_command_schema(command: str) -> list[str]:
    """Get allowed parameters for a command.

    Args:
        command: The command/action name.

    Returns:
        List of allowed parameter names.
    """
    return _COMMAND_SCHEMAS.get(command, [])
