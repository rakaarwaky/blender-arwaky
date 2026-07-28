"""Aggregate contract for the mcp feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_mcp_tool_exposure_protocol import McpToolExposureProtocol
from .contract_server_discovery_protocol import ServerDiscoveryProtocol
from .contract_server_execute_protocol import ServerExecuteProtocol
from .contract_server_health_protocol import ServerHealthProtocol
from .contract_server_response_protocol import ServerResponseProtocol

__all__ = [
    "McpToolExposureProtocol",
    "ServerDiscoveryProtocol",
    "ServerExecuteProtocol",
    "ServerHealthProtocol",
    "ServerResponseProtocol",
]
