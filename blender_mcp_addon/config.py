"""Configuration loader for Blender MCP addon."""

import os

import yaml


def get_config(key=None, default=None):
    """Load config from YAML file.

    Args:
        key: Dot-notation key (e.g. "server.port"). Returns whole config if None.
        default: Value to return if key not found.
    """
    config_path = os.environ.get("BLENDERMCP_CONFIG_PATH")
    if not config_path:
        # Try common locations
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(addon_dir, "..", "..", "config.yaml")

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        config = {}

    if key is None:
        return config

    # Navigate dot-notation keys
    value = config
    for part in key.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return default
        if value is None:
            return default

    return value
