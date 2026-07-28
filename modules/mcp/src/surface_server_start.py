"""BlenderArwaky MCP Server - Modularized

FR-MCP-001: Expose MCP Tools — main() registers all tools/prompts via SurfaceHandler
FR-MCP-002: Route Tool Calls — ServerInstanceHandler.get_mcp_instance() wires routing to agent container
FR-MCP-003: Format MCP Responses — MCP server wraps all responses in Prompt type

Main entry point that runs the MCP server.
"""

import logging
import sys

from modules.mcp.src.bootstrap import ServerBootstrapManager

from .surface_server_instance import ServerInstanceHandler

# --- Logging configuration ---
logger = logging.getLogger("BlenderMCPServer")


class ServerStartHandler:
    """Handler for server startup sequence."""

    """Handler for server startup and entry point."""

    @staticmethod
    def _setup_logging() -> None:
        """Set up logging with config via capability layer."""
        log_file = ServerBootstrapManager.resolve_log_file()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)],
        )

    @staticmethod
    def main() -> None:
        """Run the MCP server (stdio or SSE). Register all surfaces."""
        ServerStartHandler._setup_logging()
        mcp = ServerInstanceHandler.get_mcp_instance()

        # NOTE: Tools and prompts are already registered inside
        # get_mcp_instance() — do NOT re-register here.

        transport, host, port_str = ServerBootstrapManager.resolve_transport_config()

        if transport == "sse":
            mcp.settings.host = host
            mcp.settings.port = int(port_str) if port_str.isdigit() else 8000
            mcp.settings.log_level = "INFO"
            logger.info(f"Starting BlenderArwaky SSE server on {host}:{port_str}")
            mcp.run(transport="sse")
        else:
            mcp.run()
