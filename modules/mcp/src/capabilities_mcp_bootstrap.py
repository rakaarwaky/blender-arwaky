"""MCP bootstrap capabilities — server lifecycle utilities."""

from __future__ import annotations

from modules.mcp.src.utility_mcp_bootstrap import (
    record_startup,
    resolve_log_file,
    resolve_transport_config,
)
from modules.shared.src.common.taxonomy_core_vo import Host, PortNumber, ServerName
from modules.shared.src.mcp.contract_mcp_protocol import McpSchemaProtocol


class ServerBootstrapManager(McpSchemaProtocol):
    """Capability manager for MCP server lifecycle configuration."""

    async def get_tool_schemas(self) -> list[dict[str, object]]:
        """Return tool schema list."""
        return []

    async def get_catalog_version(self) -> str:
        """Return dispatcher catalog version for drift detection."""
        return "1.0.0"

    @staticmethod
    def resolve_log_file() -> str:
        return resolve_log_file()

    @staticmethod
    def resolve_transport_config(server_name: ServerName | None = None) -> tuple[str, Host, PortNumber]:
        return resolve_transport_config(server_name)


__all__ = [
    "ServerBootstrapManager",
    "record_startup",
    "resolve_log_file",
    "resolve_transport_config",
]
