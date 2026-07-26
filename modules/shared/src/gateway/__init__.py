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
    CodeExecutionVO,
    CodeExecutionResultVO,
    ConnectionState,
    ConnectionConfigVO,
    ConnectionResultVO,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationResultVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportResultVO,
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
    "ConnectionConfigVO",
    "ConnectionResultVO",
    "ConnectionStatusVO",
    "TransportMessageVO",
    "TransportResultVO",
    "SceneOperationVO",
    "SceneOperationResultVO",
    "QueueStatusVO",
    "CodeExecutionVO",
    "CodeExecutionResultVO",
]
