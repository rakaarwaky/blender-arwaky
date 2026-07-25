"""Server domain — taxonomy, contracts, and constants for Blender TCP communication.

Taxonomy: VOs (ConnectionStatus, ExecutionResult, TaskStatus, ConnectionConfig),
errors (SecurityViolationError, ExecutionTimeoutError, etc.), and constants.

Contracts: IBlenderServerAggregate — unified facade for connection lifecycle
and code execution operations. Implemented by Agent layer.

Protocols: IBlenderConnectionProtocol, IBlenderSocketAdapterProtocol,
ICodeExecutionProtocol, IExecutionQueueProtocol, ITaskManagerProtocol
— implemented by Capabilities.
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
)
from .taxonomy_server_error import (
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
    QueueConfig,
    RetryPolicy,
    TaskManagerConfig,
    TaskStatus,
    TaskState,
)

# ─── Contracts (Aggregate — single unified facade) ─────────────

from .contract_server_aggregate import IBlenderServerAggregate

# ─── Contracts (Protocols — implemented by Capabilities) ──────

from .contract_code_execution_protocol import ICodeExecutionProtocol
from .contract_connection_protocol import IBlenderConnectionProtocol
from .contract_socket_adapter_protocol import IBlenderSocketAdapterProtocol
from .contract_command_protocol import IBlenderCommandProtocol
from .contract_queue_protocol import IExecutionQueueProtocol
from .contract_task_manager_protocol import ITaskManagerProtocol

# ─── Utility (stateless standalone functions) ─────────────────

from .utility_server_io import (
    format_bytes,
    generate_temp_path,
    is_safe_path,
    read_file_bytes,
    sanitize_filename,
    safe_remove,
    truncate_bytes,
    truncate_text,
    write_file_bytes,
    write_file_text,
)
from .utility_server_message import (
    encode_message,
    decode_message_header,
    decode_message_payload,
    build_request,
    parse_response,
)
from .utility_server_string import (
    camel_to_snake,
    contains_any,
    ends_with_any,
    escape_json_string,
    is_valid_python_identifier,
    normalize_newlines,
    safe_decode,
    safe_encode,
    safe_float,
    safe_int,
    sanitize_whitespace,
    starts_with_any,
    truncate_string,
)
from .utility_server_time import (
    calculate_deadline,
    format_duration,
    is_past_deadline,
    ms_to_seconds,
    remaining_ms,
    seconds_to_ms,
)
from .utility_server_validator import validate_code_ast, check_payload_size

__all__ = [
    # ─── Taxonomy ───────────────────────────────────────────────
    "ConnectionConfig",
    "ConnectionStatus",
    "ExecutionErrorDetail",
    "ExecutionResult",
    "ExecutionStatus",
    "HeartbeatConfig",
    "QueueConfig",
    "RetryPolicy",
    "TaskManagerConfig",
    "TaskStatus",
    "TaskState",
    # ─── Constants ──────────────────────────────────────────────
    "TRANSPORT_SOCKET",
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
    # ─── Contracts (Aggregate) ──────────────────────────────────
    "IBlenderServerAggregate",
    # ─── Contracts (Protocols) ──────────────────────────────────
    "IBlenderCommandProtocol",
    "IBlenderConnectionProtocol",
    "ICodeExecutionProtocol",
    "IBlenderSocketAdapterProtocol",
    "IExecutionQueueProtocol",
    "ITaskManagerProtocol",
    # ─── Utility ────────────────────────────────────────────────
    "validate_code_ast",
    "check_payload_size",
    "encode_message",
    "decode_message_header",
    "decode_message_payload",
    "build_request",
    "parse_response",
    # IO helpers
    "generate_temp_path",
    "read_file_bytes",
    "write_file_bytes",
    "write_file_text",
    "safe_remove",
    "truncate_bytes",
    "truncate_text",
    "format_bytes",
    "sanitize_filename",
    "is_safe_path",
    # Time helpers
    "ms_to_seconds",
    "seconds_to_ms",
    "format_duration",
    "calculate_deadline",
    "is_past_deadline",
    "remaining_ms",
    # String helpers
    "sanitize_whitespace",
    "normalize_newlines",
    "truncate_string",
    "safe_decode",
    "safe_encode",
    "starts_with_any",
    "ends_with_any",
    "contains_any",
    "safe_int",
    "safe_float",
    "camel_to_snake",
    "snake_to_camel",
    "escape_json_string",
    "is_valid_python_identifier",
]
