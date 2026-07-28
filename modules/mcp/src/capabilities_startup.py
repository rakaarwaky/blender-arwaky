"""BlenderArwaky MCP Server - Modularized

Main entry point that runs the MCP server.
"""

import logging
import sys

from modules.shared.src.common.taxonomy_core_vo import SuccessFlag, ToolName
from modules.shared.src.mcp.contract_discovery_protocol import ServerDiscoveryProtocol
from modules.shared.src.mcp.contract_execute_protocol import ServerExecuteProtocol
from modules.shared.src.mcp.contract_health_protocol import ServerHealthProtocol
from modules.shared.src.mcp.contract_mcp_tool_exposure_protocol import McpToolExposureProtocol
from modules.shared.src.mcp.contract_response_protocol import ServerResponseProtocol
from modules.mcp.src.bootstrap import ServerBootstrapManager

from .capabilities_lifecycle import ServerInstanceHandler

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
