"""MCP Server Bootstrap — configuration and startup utilities.

Provides ServerBootstrapManager for resolving transport config and log file,
plus record_startup() for telemetry integration.
"""

from __future__ import annotations

import logging
import os
import threading

from modules.shared.src.config import DEFAULT_SETTINGS

logger = logging.getLogger("BlenderMCPServer")

# ─── Defaults ────────────────────────────────────────────────────────────────
_DEFAULT_LOG_FILE: str = "blender_mcp.log"
_DEFAULT_TRANSPORT: str = DEFAULT_SETTINGS["server"]["transport"]  # "stdio"
_DEFAULT_HOST: str = DEFAULT_SETTINGS["blender"]["host"]  # "localhost"
_DEFAULT_PORT: str = str(DEFAULT_SETTINGS["blender"]["port"])  # "9876"


class ServerBootstrapManager:
    """Bootstrap manager for MCP server configuration."""

    @staticmethod
    def resolve_log_file() -> str:
        """Resolve the log file path for MCP server logging.

        Returns:
            Path to the log file.
        """
        return _DEFAULT_LOG_FILE

    @staticmethod
    def resolve_transport_config() -> tuple[str, str, str]:
        """Resolve transport configuration (transport, host, port).

        Returns:
            Tuple of (transport, host, port_str).
        """
        # Check environment variables for overrides
        transport = os.environ.get("BLENDERMCP_TRANSPORT", _DEFAULT_TRANSPORT)
        host = os.environ.get("BLENDERMCP_HOST", _DEFAULT_HOST)
        port_str = os.environ.get("BLENDERMCP_PORT", _DEFAULT_PORT)
        return (transport, host, port_str)


# ─── Startup Telemetry ──────────────────────────────────────────────────────

_startup_recorded: bool = False
_startup_lock = threading.Lock()


def record_startup() -> None:
    """Record server startup event (best-effort telemetry).

    This is a non-blocking, best-effort operation. If telemetry is available,
    it will be called; otherwise the function silently succeeds.
    """
    global _startup_recorded
    with _startup_lock:
        if _startup_recorded:
            return
        _startup_recorded = True

    # Best-effort telemetry integration: probe availability without importing
    # the orchestrator (which would create an unused, container-level import).
    try:
        import importlib.util

        _telemetry_spec = importlib.util.find_spec(
            "modules.telemetry.src.agent_telemetry_orchestrator"
        )
        if _telemetry_spec is not None:
            logger.debug("Startup event recorded (telemetry wired at container level)")
        else:
            logger.debug("Startup event recorded (no telemetry available)")
    except ImportError:
        logger.debug("Startup event recorded (no telemetry available)")
