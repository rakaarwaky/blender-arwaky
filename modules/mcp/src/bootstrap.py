"""MCP Server Bootstrap — startup and system utilities."""

import logging
import os
from pathlib import Path

logger = logging.getLogger("BlenderMCPServer")


class ServerBootstrapManager:
    """Manages server bootstrap and system utilities."""

    @staticmethod
    def resolve_log_file() -> str:
        """Resolve log file path."""
        log_dir = Path.home() / ".config" / "blender-arwaky" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return str(log_dir / "server.log")

    @staticmethod
    def resolve_transport_config() -> tuple[str, str, str]:
        """Resolve transport config (transport, host, port)."""
        transport = os.getenv("MCP_TRANSPORT", "stdio")
        host = os.getenv("MCP_HOST", "localhost")
        port = os.getenv("MCP_PORT", "8000")
        return transport, host, port


def record_startup() -> None:
    """Record server startup telemetry."""
    logger.info("Server startup recorded")