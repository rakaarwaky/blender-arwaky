"""Utility: Command argument schema validation and catalog for Blender commands.

Stateless standalone functions that validate command arguments
against a catalog-driven schema before sending to Blender.
Domain-agnostic — reusable across modules.
Implements v2.0.0 command catalog metadata per Section 4.7.
"""

from __future__ import annotations

from typing import Any

from ..common.taxonomy_domain_error import ValidationError
from .taxonomy_server_vo import ServerCommandSpec

# ─── Command Catalog ──────────────────────────────────────────────

_COMMAND_CATALOG: frozenset[ServerCommandSpec] = frozenset((
    ServerCommandSpec(
        name="ping",
        required_params=(),
        optional_params=(),
        param_types=ServerCommandSpec._make_param_types({}),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=False,
        background_allowed=False,
    ),
    ServerCommandSpec(
        name="get_status",
        required_params=(),
        optional_params=(),
        param_types=ServerCommandSpec._make_param_types({}),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=False,
        background_allowed=False,
    ),
    ServerCommandSpec(
        name="get_version",
        required_params=(),
        optional_params=(),
        param_types=ServerCommandSpec._make_param_types({}),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=False,
        background_allowed=False,
    ),
    ServerCommandSpec(
        name="get_scene_info",
        required_params=(),
        optional_params=("include_objects", "include_data_blocks"),
        param_types=ServerCommandSpec._make_param_types({"include_objects": "bool", "include_data_blocks": "bool"}),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=False,
        background_allowed=False,
    ),
    ServerCommandSpec(
        name="get_object_info",
        required_params=("name",),
        optional_params=("include_data", "include_children"),
        param_types=ServerCommandSpec._make_param_types({"name": "str", "include_data": "bool", "include_children": "bool"}),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=False,
        background_allowed=False,
    ),
    ServerCommandSpec(
        name="get_screenshot",
        required_params=(),
        optional_params=("max_size", "view_angle", "shading_mode", "show_overlays", "focus_object"),
        param_types=ServerCommandSpec._make_param_types({
            "max_size": "int",
            "view_angle": "float",
            "shading_mode": "str",
            "show_overlays": "bool",
            "focus_object": "str",
        }),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=False,
        background_allowed=False,
    ),
    ServerCommandSpec(
        name="execute_code",
        required_params=("code",),
        optional_params=("timeout_ms",),
        param_types=ServerCommandSpec._make_param_types({"code": "str", "timeout_ms": "int"}),
        default_timeout_ms=30000.0,
        max_timeout_ms=120000.0,
        idempotent=False,
        mutates_scene=True,
        background_allowed=True,
    ),
    ServerCommandSpec(
        name="ensure_workspace",
        required_params=(),
        optional_params=("temp_directory", "filename_prefix"),
        param_types=ServerCommandSpec._make_param_types({"temp_directory": "str", "filename_prefix": "str"}),
        default_timeout_ms=5000.0,
        max_timeout_ms=60000.0,
        idempotent=True,
        mutates_scene=True,
        background_allowed=False,
    ),
))

# Build lookup maps
_command_spec_map: dict[str, ServerCommandSpec] = {spec.name: spec for spec in _COMMAND_CATALOG}


def get_command_spec(command: str) -> ServerCommandSpec:
    """Get command specification by name.

    Raises ValidationError if command is unknown.

    Args:
        command: The command/action name.

    Returns:
        ServerCommandSpec with metadata.

    Raises:
        ValidationError: If command is not in the catalog.
    """
    if command not in _command_spec_map:
        raise ValidationError(message=f"Unknown command: {command}", code="unknown_command")
    return _command_spec_map[command]


def validate_command_args(command: str, params: dict[str, Any] | None) -> None:
    """Validate command arguments against catalog schema.

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
    spec = get_command_spec(command)
    allowed_keys = set(spec.required_params) | set(spec.optional_params)

    if params is None:
        # Check required params
        if spec.required_params:
            raise ValidationError(
                message=f"Missing required parameter(s): {', '.join(spec.required_params)}",
                code="validation_error",
                details={"missing": list(spec.required_params)},
            )
        return

    if not isinstance(params, dict):
        raise ValidationError(message="Command arguments must be a dictionary")

    # Check for unknown keys
    for key in params:
        if key not in allowed_keys:
            raise ValidationError(
                message=f"Unknown parameter '{key}' for command '{command}'",
                code="validation_error",
            )

    # Check required parameters are present
    missing = [p for p in spec.required_params if p not in params]
    if missing:
        raise ValidationError(
            message=f"Missing required parameter(s): {', '.join(missing)}",
            code="validation_error",
            details={"missing": missing},
        )


def is_scene_mutating(command: str) -> bool:
    """Check if a command mutates Blender scene state.

    Args:
        command: The command name.

    Returns:
        True if the command mutates scene, False otherwise.
    """
    try:
        return get_command_spec(command).mutates_scene
    except ValidationError:
        # Unknown commands default to not mutating (they'll fail later)
        return False


def effective_command_timeout_ms(command: str, requested_timeout_ms: float | None) -> float:
    """Calculate the effective timeout for a command.

    Uses command spec default if caller provides no timeout.
    Rejects caller-provided timeout exceeding max.

    Args:
        command: The command name.
        requested_timeout_ms: Caller-provided timeout, or None for default.

    Returns:
        Effective timeout in milliseconds.

    Raises:
        ValidationError: If requested timeout exceeds spec max.
    """
    spec = get_command_spec(command)
    if requested_timeout_ms is None:
        return spec.default_timeout_ms
    if requested_timeout_ms > spec.max_timeout_ms:
        raise ValidationError(
            message=f"Requested timeout {requested_timeout_ms}ms exceeds max {spec.max_timeout_ms}ms",
            code="validation_error",
        )
    return requested_timeout_ms


def get_command_schema(command: str) -> list[str]:
    """Get allowed parameters for a command (legacy alias).

    Args:
        command: The command name.

    Returns:
        List of allowed parameter names.

    Raises:
        ValidationError: If command is not in the catalog.
    """
    spec = get_command_spec(command)
    return list(spec.required_params) + list(spec.optional_params)
