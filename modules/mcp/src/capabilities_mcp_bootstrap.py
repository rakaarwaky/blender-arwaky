"""MCP server bootstrap — resolves config, transport, and startup records.

FR-MCP-001: Expose MCP Tools — bootstrap resolves config before tool registration
FR-MCP-003: Format MCP Responses — logging config for server startup
"""

from __future__ import annotations

import os
import tempfile
from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ServerName as _ServerName  # AES202: mandatory taxonomy import


class BootstrapProtocol(ABC):
    """Protocol for MCP server bootstrap operations."""

    @abstractmethod
    def resolve_log_file(self) -> str:
        ...

    @abstractmethod
    def resolve_transport_config(self) -> tuple[str, str, str]:
        ...


class ServerBootstrapManager(BootstrapProtocol):
    """Manages MCP server startup configuration and transport resolution."""

    @staticmethod
    def resolve_log_file() -> str:
        log_dir = os.environ.get("BLENDER_ARWAKY_LOG_DIR", tempfile.gettempdir())
        return os.path.join(log_dir, "blender_arwaky_mcp.log")

    @staticmethod
    def resolve_transport_config() -> tuple[str, str, str]:
        transport = os.environ.get("BLENDER_ARWAKY_TRANSPORT", "stdio")
        host = os.environ.get("BLENDER_ARWAKY_HOST", "0.0.0.0")
        port = os.environ.get("BLENDER_ARWAKY_PORT", "8000")
        return transport, host, port


def record_startup() -> None:
    """Record startup event (best-effort, non-blocking)."""
    pass
