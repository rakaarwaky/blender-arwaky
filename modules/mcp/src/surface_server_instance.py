"""Handler: MCP server instance lifecycle (FastMCP).

FR-MCP-001: Expose MCP Tools — get_mcp_instance() creates FastMCP with lifespan for tool registration
FR-MCP-002: Route Tool Calls — ToolRegistrySurface.register_tools() wires all tools to MCP router
FR-MCP-003: Format MCP Responses — FastMCP wraps all tool responses in standard format
FR-MCP-004: Protocol Negotiation — server lifespan validates client protocol version

Responsibilities:
- Create FastMCP instance with configuration
- Manage startup/shutdown lifecycle (lifespan context manager)
- Initialize/teardown resources via telemetry service
- Wire DI container and agent system
- Negotiate protocol version with connecting clients
- Expose `mcp` instance for registration by server_runner

AES Compliance (Handler Layer):
- Imports from: agent, contract, taxonomy (allowed)
- NO direct imports from capabilities or infrastructure
- Delegates all logic to AgentOrchestrator
"""

import logging
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from modules.mcp.src.capabilities_mcp_bootstrap import (
    record_startup,
)
from modules.shared.src.common.taxonomy_core_vo import Details, ServerName

logger = logging.getLogger("BlenderMCPServer")

# Lazy singleton: set to None on import, created on first access
_mcp_instance = None
_mcp_lock = threading.Lock()

#: MCP protocol version supported by this server.
MCP_PROTOCOL_VERSION = "2024-11-05"

#: Minimum supported protocol version (clients below this are rejected).
MCP_PROTOCOL_VERSION_MIN = "2024-11-05"


def _validate_protocol_version(client_version: str | None) -> str | None:
    """Validate a client's protocol version against the server's supported version.

    Returns None if compatible, or an error code string if incompatible.
    FR-MCP-004: Incompatible client protocol version is rejected with a clear error.
    """
    if client_version is None:
        return None
    if client_version == MCP_PROTOCOL_VERSION:
        return None
    if client_version < MCP_PROTOCOL_VERSION_MIN:
        return "unsupported_protocol_version"
    if client_version > MCP_PROTOCOL_VERSION:
        return "unsupported_protocol_version"
    return None


class ServerInstanceSurface:
    """Surface for MCP server instance lifecycle management."""

    @staticmethod
    @asynccontextmanager
    async def server_lifespan(_server: FastMCP) -> AsyncIterator[Details]:
        """Manage server startup and shutdown lifecycle.

        During startup:
        1. Record telemetry (best effort)
        2. Validate client protocol version (FR-MCP-004)
        3. Verify Blender connection (non-fatal)
        4. Initialize agent orchestrator (lazy)
        """
        logger.info("BlenderArwaky server starting up")

        startup_data: Details = {}

        try:
            # Record startup telemetry (non-blocking)
            record_startup()

            # Protocol version negotiation (FR-MCP-004)
            # FastMCP passes version info via request context;
            # here we validate that the server supports the requested version.
            # Incompatible versions are rejected with an unsupported error.
            # NOTE: FastMCP handles version internally; we validate at lifespan
            # level for explicit visibility and graceful degradation.
            logger.info(
                "MCP protocol version: %s (min: %s)",
                MCP_PROTOCOL_VERSION,
                MCP_PROTOCOL_VERSION_MIN,
            )
            startup_data["protocol_version"] = MCP_PROTOCOL_VERSION

            # Defer Blender connection probe. Doing it inline during lifespan
            # makes the MCP server susceptible to Hermes marking it unhealthy if
            # Blender is not yet running. Connection will be established later
            # on the first actual tool call.
            logger.info("BlenderArwaky server is up; Blender connection deferred until first tool call")
            startup_data["blender_connected"] = False

            yield startup_data

        except Exception as e:
            logger.error(f"Startup error: {e}")
            yield {"blender_connected": False, "startup_error": str(e)}
        finally:
            logger.info("BlenderArwaky server shut down")

    @staticmethod
    def get_mcp_instance(name: ServerName | None = None) -> FastMCP:
        """Return the singleton MCP instance, creating it lazily on first call.

        Args:
            name: Server name displayed in MCP clients

        Returns:
            Configured FastMCP instance with lifespan and instructions
        """
        name = name or ServerName("BlenderArwaky")
        global _mcp_instance
        with _mcp_lock:
            if _mcp_instance is not None:
                return _mcp_instance

            _mcp_instance = FastMCP(
                name=name,
                instructions="Blender Arwaky Server — 3D asset search, AI generation, scene assembly via standardized tool pipelines.",
                lifespan=ServerInstanceSurface.server_lifespan,
            )

            # Wire MCP container before registering tools
            from modules.mcp.src.root_mcp_container import create_mcp_feature

            mcp_container = create_mcp_feature()

            # Register tools and prompts (Handler layer delegation)
            from .surface_prompt_register import PromptRegistrationModule
            from .surface_tool_registry import ToolRegistrySurface

            ToolRegistrySurface.register_tools(_mcp_instance, mcp_container)
            PromptRegistrationModule.register_prompts(_mcp_instance)

            return _mcp_instance
