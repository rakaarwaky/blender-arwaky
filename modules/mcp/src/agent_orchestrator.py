"""Agent: MCP feature orchestrator.

Coordinates MCP server lifecycle, tool registration, and AI agent communication.
"""

import logging
from typing import Any

from modules.shared.src.mcp.contract_mcp_aggregate import (
    ServerDiscoveryProtocol,
    ServerExecuteProtocol,
    ServerHealthProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class McpOrchestrator:
    """Orchestrates MCP server operations."""

    def __init__(self, server: Any):
        self._server = server

    def start(self) -> None:
        """Start MCP server."""
        self._server.start()

    def register_tools(self, mcp: Any) -> None:
        """Register MCP tools."""
        self._server.register_tools(mcp)

    def shutdown(self) -> None:
        """Shutdown MCP server."""
        self._server.shutdown()
