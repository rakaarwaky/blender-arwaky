"""Root: MCP surface composition container.

Wires MCP tool handlers to the MCP server instance via contract protocols.
Provides a single DI entry point so tools depend on contracts, not root containers.
"""

from __future__ import annotations

import logging

from modules.mcp.src.capabilities_response_formatter import McpResponseImpl
from modules.mcp.src.capabilities_routing_proxy import McpRoutingImpl
from modules.shared.src.mcp.contract_mcp_protocol import (
    McpResponseProtocol,
    McpRoutingProtocol,
    McpSchemaProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class McpContainer:
    """Dependency injection container for the MCP surface module.

    Provides contract-protocol instances to tool handlers.
    """

    def __init__(self) -> None:
        self._routing: McpRoutingProtocol | None = None
        self._schema: McpSchemaProtocol | None = None
        self._response: McpResponseProtocol | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire MCP surface to contract protocols."""
        if self._wired:
            return

        logger.info("Wiring MCP surface module")



        # Create protocol implementations (delegating to owning features)
        self._routing = McpRoutingImpl()
        self._schema = McpResponseImpl()  # schema and response share same implementation for now
        self._response = McpResponseImpl()

        self._wired = True
        logger.info("MCP surface module wired successfully")

    @property
    def routing(self) -> McpRoutingProtocol:
        if not self._wired or self._routing is None:
            raise RuntimeError("McpContainer not wired — call wire() first")
        return self._routing

    @property
    def schema(self) -> McpSchemaProtocol:
        if not self._wired or self._schema is None:
            raise RuntimeError("McpContainer not wired — call wire() first")
        return self._schema

    @property
    def response(self) -> McpResponseProtocol:
        if not self._wired or self._response is None:
            raise RuntimeError("McpContainer not wired — call wire() first")
        return self._response


def create_mcp_feature() -> McpContainer:
    """Factory function to create and wire the MCP surface module."""
    container = McpContainer()
    container.wire()
    return container
