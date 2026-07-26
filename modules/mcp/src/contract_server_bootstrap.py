"""Contract: ServerBootstrapAggregate (AES _aggregate suffix).

Specialized structural contract for the agent layer.
Defines the server bootstrap interface for MCP server lifecycle management.
"""

from abc import ABC

from modules.shared.src.common.taxonomy_core_vo import FilePath, ObjectName


class ServerBootstrapManagerAggregate(ABC):
    """Interface for ServerBootstrapManager."""

    _contract_name: ObjectName = ObjectName("ServerBootstrapManagerAggregate")
    _compliance: FilePath | None = None

    @classmethod
    def get_contract_name(cls) -> ObjectName:
        return cls._contract_name