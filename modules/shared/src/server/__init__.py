"""Server domain — taxonomy, contracts, and constants for Blender TCP/stdio communication.

Taxonomy: VOs (ConnectionStatus, ExecutionResult, TaskStatus, ConnectionConfig),
errors (SecurityViolationError, ExecutionTimeoutError, etc.), and constants.

Contracts: IBlenderServerAggregate — unified facade for connection lifecycle
and code execution operations. Implemented by Agent layer.

Protocols: IBlenderConnectionProtocol, IBlenderSocketAdapterProtocol,
ICodeExecutionProtocol — implemented by Capabilities.
"""

# ─── Taxonomy ──────────────────────────────────────────────────

from .taxonomy_server_constant import (
    CONNECTION_TIMEOUT_SECONDS,
    DEFAULT_COMMAND_TIMEOUT_MS,
    DEFAULT_EXECUTION_TIMEOUT_MS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_QUEUE_WAIT_TIMEOUT_MS,
    DEFAULT_TASK_RETENTION_SECONDS,
    HEARTBEAT_FAILURE_THRESHOLD,
    HEARTBEAT_INTERVAL_SECONDS,
    MAX_CODE_PAYLOAD_BYTES,
    MAX_RECONNECT_ATTEMPTS,
    QUEUE_MAX_DEPTH,
    RETRY_BASE_DELAY_SECONDS,
    RETRY_MAX_DELAY_SECONDS,
    TRANSPORT_SOCKET,
    TRANSPORT_STDIO,
)
from .taxonomy_server_error import (
    AdapterSurfaceError,
    AuthenticationError,
    BlenderConnectionExhausted,
    CommandTimeoutError,
    ConnectionClosedError,
    ConnectionConfigError,
    ExecutionTimeoutError,
    ProtocolVersionMismatchError,
    QueueFullError,
    QueueTimeoutError,
    SecurityViolationError,
    TaskNotFoundError,
)
from .taxonomy_server_vo import (
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    ExecutionStatus,
    HeartbeatConfig,
    RetryPolicy,
    TaskStatus,
    TaskState,
)

# ─── Contracts (Aggregate — single unified facade) ─────────────

from .contract_server_aggregate import IBlenderServerAggregate

# ─── Contracts (Protocols — implemented by Capabilities) ──────

from .contract_code_execution_protocol import ICodeExecutionProtocol
from .contract_connection_protocol import IBlenderConnectionProtocol
from .contract_socket_adapter_protocol import IBlenderSocketAdapterProtocol

# ─── Utility (stateless standalone functions) ─────────────────

from .utility_server_validator import validate_code_ast, check_payload_size
from .utility_server_queue import ExecutionQueue, QueueConfig
from .utility_server_task_manager import TaskManager, TaskManagerConfig
from .utility_server_message import encode_message, decode_message_header, decode_message_payload, build_request, parse_response

__all__ = [
    # ─── Taxonomy ───────────────────────────────────────────────
    "ConnectionConfig",
    "ConnectionStatus",
    "ExecutionErrorDetail",
    "ExecutionResult",
    "ExecutionStatus",
    "HeartbeatConfig",
    "RetryPolicy",
    "TaskStatus",
    "TaskState",
    # ─── Constants ──────────────────────────────────────────────
    "TRANSPORT_SOCKET",
    "TRANSPORT_STDIO",
    "CONNECTION_TIMEOUT_SECONDS",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_EXECUTION_TIMEOUT_MS",
    "DEFAULT_COMMAND_TIMEOUT_MS",
    "MAX_CODE_PAYLOAD_BYTES",
    "HEARTBEAT_INTERVAL_SECONDS",
    "HEARTBEAT_FAILURE_THRESHOLD",
    "MAX_RECONNECT_ATTEMPTS",
    "RETRY_BASE_DELAY_SECONDS",
    "RETRY_MAX_DELAY_SECONDS",
    "QUEUE_MAX_DEPTH",
    "DEFAULT_QUEUE_WAIT_TIMEOUT_MS",
    "DEFAULT_TASK_RETENTION_SECONDS",
    # ─── Errors ─────────────────────────────────────────────────
    "SecurityViolationError",
    "ExecutionTimeoutError",
    "QueueFullError",
    "QueueTimeoutError",
    "CommandTimeoutError",
    "TaskNotFoundError",
    "ConnectionConfigError",
    "AuthenticationError",
    "ProtocolVersionMismatchError",
    "ConnectionClosedError",
    "BlenderConnectionExhausted",
    "AdapterSurfaceError",
    # ─── Contracts (Aggregate) ──────────────────────────────────
    "IBlenderServerAggregate",
    # ─── Contracts (Protocols) ──────────────────────────────────
    "IBlenderConnectionProtocol",
    "ICodeExecutionProtocol",
    "IBlenderSocketAdapterProtocol",
    # ─── Utility ────────────────────────────────────────────────
    "validate_code_ast",
    "check_payload_size",
    "ExecutionQueue",
    "QueueConfig",
    "TaskManager",
    "TaskManagerConfig",
    "encode_message",
    "decode_message_header",
    "decode_message_payload",
    "build_request",
    "parse_response",
]
