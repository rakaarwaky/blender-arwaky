"""Root: Server feature entry point.

Bootstraps the server feature by creating the container,
wiring dependencies, and starting the connection.
"""

from __future__ import annotations

import logging

from modules.shared.src.server import ConnectionConfig
from modules.server.src.root_server_container import ServerContainer

logger = logging.getLogger("BlenderMCPServer")


def create_server_entry(config: ConnectionConfig | None = None) -> ServerContainer:
    """Create and wire the server feature container.

    Returns the wired container ready for use.
    """
    container = ServerContainer(config)
    container.wire()
    logger.info("Server feature entry point created")
    return container


async def start_server(config: ConnectionConfig | None = None) -> ServerContainer:
    """Bootstrap and start the server feature.

    Creates container, wires dependencies, and establishes
    connection to Blender.
    """
    container = create_server_entry(config)

    # Attempt initial connection
    try:
        await container.orchestrator.connect(config or ConnectionConfig(transport_type="socket"))
        logger.info("Server connected to Blender")
    except Exception as e:
        logger.warning("Initial connection failed: %s — will retry on first request", e)

    return container
