"""MCP DI Container — wires capabilities to contracts."""

import logging
from typing import Any

logger = logging.getLogger("BlenderMCPServer")

_container: Any = None


def get_container() -> Any:
    """Get or create the DI container singleton."""
    global _container
    if _container is None:
        _container = _create_container()
    return _container


def _create_container() -> Any:
    """Create and wire the DI container."""
    from modules.config.src.utility_config_loader import get_config

    from modules.gateway.src.capabilities_connection import BlenderConnection

    config = get_config
    blender_conn = BlenderConnection.create_from_config(config=config)

    return {"blender_connection": blender_conn, "config": config}