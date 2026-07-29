"""Gateway domain — re-exports for contract protocols and taxonomy types.

AES305: __all__ removed to avoid duplication with shared/src/__init__.py
which already re-exports the same symbols.
"""

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
