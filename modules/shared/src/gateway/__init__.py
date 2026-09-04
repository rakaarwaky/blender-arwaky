"""Gateway domain — re-exports for contract protocols and taxonomy types."""

from .capabilities_socket_client import BlenderSocketClient
from .contract_code_execution_protocol import CodeExecutionProtocol
from .contract_connection_protocol import ConnectionProtocol
from .contract_maintenance_protocol import ConnectionMaintenanceProtocol
from .contract_scene_queue_protocol import SceneQueueProtocol
from .contract_transport_protocol import TransportProtocol
from .taxonomy_gateway_error import (
    AuthenticationError,
    ChannelConflictError,
    ConnectionError,
    GatewayError,
    GatewayExecutionError,
    GatewayProviderError,
    GatewayValidationError,
    PayloadLimitError,
    ProtocolVersionMismatchError,
    SecurityViolationError,
    TimeoutError,
    TransportParseError,
)
from .taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionConfigVO,
    ConnectionOutcomeVO,
    ConnectionState,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
    TransportType,
)

__all__ = [
    "AuthenticationError",
    "BlenderSocketClient",
    "ChannelConflictError",
    "CodeExecutionOutcomeVO",
    "CodeExecutionProtocol",
    "CodeExecutionVO",
    "ConnectionConfigVO",
    "ConnectionError",
    "ConnectionMaintenanceProtocol",
    "ConnectionOutcomeVO",
    "ConnectionProtocol",
    "ConnectionState",
    "ConnectionStatusVO",
    "GatewayError",
    "GatewayExecutionError",
    "GatewayProviderError",
    "GatewayValidationError",
    "PayloadLimitError",
    "ProtocolVersionMismatchError",
    "QueueStatusVO",
    "SceneOperationOutcomeVO",
    "SceneOperationProtocol",
    "SceneOperationVO",
    "SceneQueueProtocol",
    "SecurityViolationError",
    "TimeoutError",
    "TransportMessageVO",
    "TransportOutcomeVO",
    "TransportParseError",
    "TransportProtocol",
    "TransportType",
]
