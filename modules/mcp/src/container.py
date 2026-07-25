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
    from modules.server.src.capabilities_blender_connection import BlenderConnectionFactory
    from modules.config.src.contract_config import ConfigPort
    from modules.config.src.utility_config_loader import get_config

    config = get_config
    blender_factory = BlenderConnectionFactory(config=config)

    return {"blender_factory": blender_factory, "config": config}
