"""MCP bootstrap utilities — server lifecycle helpers.

Provides stateless functions for resolving transport, logging, and telemetry configuration.
"""

from __future__ import annotations

import logging
import os

from modules.shared.src.common.taxonomy_core_vo import (
    Host,
    PortNumber,
    ServerName,
)

logger = logging.getLogger("BlenderMCPServer")


def resolve_log_file() -> str:
    """Resolve log file path from config or default to user home."""
    log_dir = os.path.join(
        os.path.expanduser("~"),
        ".local",
        "share",
        "blender-arwaky",
        "logs",
    )
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "mcp_server.log")


def resolve_transport_config(server_name: ServerName | None = None) -> tuple[str, Host, PortNumber]:
    """Resolve transport configuration (transport, host, port)."""
    _ = server_name
    transport = os.environ.get("ARWAKY_MCP_TRANSPORT", "stdio")
    host = Host(os.environ.get("ARWAKY_MCP_HOST", "127.0.0.1"))
    port = PortNumber(int(os.environ.get("ARWAKY_MCP_PORT", "8080")))
    return (transport, host, port)


def record_startup() -> None:
    """Record MCP server startup telemetry (best effort)."""
    try:
        logger.info("MCP server startup recorded")
    except Exception as e:
        logger.debug("Telemetry recording failed (non-blocking): %s", e)
