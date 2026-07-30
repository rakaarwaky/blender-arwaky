"""BlenderArwaky MCP Server - Modularized

FR-MCP-001: Expose MCP Tools — main() registers all tools/prompts via SurfaceHandler
FR-MCP-002: Route Tool Calls — ServerInstanceSurface.get_mcp_instance() wires routing to agent container
FR-MCP-003: Format MCP Responses — MCP server wraps all responses in Prompt type

Main entry point that runs the MCP server.
"""

import logging
import sys

from modules.shared.src.mcp.utility_mcp_bootstrap import (
    resolve_bootstrap_config,
)

from .surface_server_instance import ServerInstanceSurface

# --- Logging configuration ---
logger = logging.getLogger("BlenderMCPServer")


class ServerStartSurface:
    """Surface for server startup sequence and entry point."""

    @staticmethod
    def _setup_logging(log_file: str) -> None:
        """Set up logging with log file path from bootstrap VO."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stderr)],
        )

    @staticmethod
    def main() -> None:
        """Run the MCP server (stdio or SSE). Register all surfaces."""
        config = resolve_bootstrap_config()
        ServerStartSurface._setup_logging(config.log_file)
        mcp = ServerInstanceSurface.get_mcp_instance()

        if config.is_sse():
            mcp.settings.host = config.host
            mcp.settings.port = config.port
            mcp.settings.log_level = "INFO"
            logger.info(f"Starting BlenderArwaky SSE server on {config.host}:{config.port}")
            mcp.run(transport="sse")
        else:
            mcp.run()

