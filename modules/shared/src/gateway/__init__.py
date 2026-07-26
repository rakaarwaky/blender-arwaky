"""Gateway domain — Taxonomy layer: VOs, Errors for connection, transport, queue, execution."""

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
    CodeExecutionRequestVO,
    CodeExecutionResultVO,
    ConnectionState,
    ConnectionRequestVO,
    ConnectionResultVO,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationResultVO,
    SceneOperationVO,
    TransportRequestVO,
    TransportResponseVO,
    TransportType,
)

__all__ = [
    # Errors
    "GatewayError",
    "ConnectionError",
    "TimeoutError",
    "ProtocolVersionMismatchError",
    "AuthenticationError",
    "ChannelConflictError",
    "SecurityViolationError",
    "TransportParseError",
    "PayloadLimitError",
    # VOs
    "ConnectionState",
    "TransportType",
    "ConnectionRequestVO",
    "ConnectionResultVO",
    "ConnectionStatusVO",
    "TransportRequestVO",
    "TransportResponseVO",
    "SceneOperationVO",
    "SceneOperationResultVO",
    "QueueStatusVO",
    "CodeExecutionRequestVO",
    "CodeExecutionResultVO",
]
