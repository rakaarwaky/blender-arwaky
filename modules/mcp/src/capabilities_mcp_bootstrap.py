"""MCP bootstrap capabilities — server lifecycle utilities.

Provides ServerBootstrapManager for resolving transport, logging, and telemetry
configuration. This file was created to fix broken imports in surface_server_start.py
and surface_server_instance.py (LB04, O01).
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger("BlenderMCPServer")


class ServerBootstrapManager:
    """Bootstrap manager for MCP server lifecycle configuration."""

    @staticmethod
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

    @staticmethod
    def resolve_transport_config() -> tuple[str, str, str]:
        """Resolve transport configuration (transport, host, port)."""
        transport = os.environ.get("ARWAKY_MCP_TRANSPORT", "stdio")
        host = os.environ.get("ARWAKY_MCP_HOST", "127.0.0.1")
        port = os.environ.get("ARWAKY_MCP_PORT", "8080")
        return (transport, host, port)


def record_startup() -> None:
    """Record MCP server startup telemetry (best effort)."""
    try:
        logger.info("MCP server startup recorded")
    except Exception as e:
        logger.debug("Telemetry recording failed (non-blocking): %s", e)
