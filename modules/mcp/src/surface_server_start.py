"""BlenderArwaky MCP Server - Modularized

FR-MCP-001: Expose MCP Tools — main() registers all tools/prompts via SurfaceHandler
FR-MCP-002: Route Tool Calls — ServerInstanceSurface.get_mcp_instance() wires routing to agent container
FR-MCP-003: Format MCP Responses — MCP server wraps all responses in Prompt type

Main entry point that runs the MCP server.
"""

import logging
import sys

from modules.mcp.src.utility_mcp_bootstrap import (
    resolve_log_file,
    resolve_transport_config,
)

from .surface_server_instance import ServerInstanceSurface

# --- Logging configuration ---
logger = logging.getLogger("BlenderMCPServer")


class ServerStartSurface:
    """Surface for server startup sequence and entry point."""

    @staticmethod
    def _setup_logging() -> None:
        """Set up logging with config via utility layer."""
        log_file = resolve_log_file()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)],
        )

    @staticmethod
    def main() -> None:
        """Run the MCP server (stdio or SSE). Register all surfaces."""
        ServerStartSurface._setup_logging()
        mcp = ServerInstanceSurface.get_mcp_instance()

        # NOTE: Tools and prompts are already registered inside
        # get_mcp_instance() — do NOT re-register here.

        transport, host, port = resolve_transport_config()

        if transport == "sse":
            mcp.settings.host = str(host)
            mcp.settings.port = int(port)

            mcp.settings.log_level = "INFO"
            logger.info(f"Starting BlenderArwaky SSE server on {host}:{port}")
            mcp.run(transport="sse")

        else:
            mcp.run()
