"""Shared action registry — aggregates all domain action schemas for CLI and MCP surfaces."""

from typing import Any

from .surface_asset_action import ASSET_ACTIONS
from .surface_config_action import CONFIG_ACTIONS
from .surface_job_action import JOB_ACTIONS
from .surface_launcher_action import LAUNCHER_ACTIONS
from .surface_object_action import OBJECT_ACTIONS
from .surface_render_action import RENDER_ACTIONS
from .surface_scene_action import SCENE_ACTIONS

ALL_ACTIONS: dict[str, dict[str, Any]] = {}
ACTION_DOMAIN: dict[str, str] = {}

for domain, actions in [
    ("scene", SCENE_ACTIONS),
    ("object", OBJECT_ACTIONS),
    ("render", RENDER_ACTIONS),
    ("asset", ASSET_ACTIONS),
    ("launcher", LAUNCHER_ACTIONS),
    ("job", JOB_ACTIONS),
    ("config", CONFIG_ACTIONS),
]:
    for action_name, schema in actions.items():
        ALL_ACTIONS[action_name] = schema
        ACTION_DOMAIN[action_name] = domain


def get_action_schema(action: str) -> dict[str, Any] | None:
    """Return the parameter schema for a given action name, or None if unknown."""
    return ALL_ACTIONS.get(action)


def get_domain_actions(domain: str) -> dict[str, dict[str, Any]]:
    """Return all actions belonging to a domain."""
    return {name: schema for name, schema in ALL_ACTIONS.items() if ACTION_DOMAIN.get(name) == domain}


def validate_action_args(action: str, args: dict[str, Any]) -> list[str]:
    """Validate args against the action schema. Returns list of error messages (empty = valid)."""
    schema = ALL_ACTIONS.get(action)
    if schema is None:
        return [f"Unknown action: {action}"]

    errors: list[str] = []
    params = schema.get("parameters", {})

    for param_name, param_spec in params.items():
        if param_spec.get("required") and param_name not in args:
            errors.append(f"Missing required parameter: {param_name}")

    for arg_name in args:
        if arg_name not in params:
            errors.append(f"Unknown parameter: {arg_name}")

    return errors
