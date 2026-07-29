"""Capability: MCP server bootstrap and lifecycle management.

FR-MCP-001: Server lifecycle (init, protocol negotiation, shutdown)
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("BlenderMCPServer")


class ServerBootstrapManager:
    """Manages MCP server bootstrap configuration and lifecycle."""

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
