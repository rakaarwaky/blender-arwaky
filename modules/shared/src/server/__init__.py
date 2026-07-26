"""Server domain — taxonomy, contracts, utilities, and capabilities for Blender v2.0.0.

Taxonomy: VOs (ConnectionStatus, ExecutionResult, TaskStatus, ServerConfig, etc.),
errors (TooManyPendingOperationsError, OperationWaitTimeoutError, etc.),
constants (CONNECTION_STATE_*, TASK_STATE_*, OPERATION_TYPE_*),
events (ServerEvent union).

Contracts: IBlenderServerAggregate, IBlenderConnectionProtocol,
ICodeExecutionProtocol, IBlenderCommandProtocol, IEventBus, IMetricsProvider,
IOperationQueueProtocol.

Utilities: validate_code_ast, check_payload_size, code_fingerprint,
validate_command_args, get_command_spec, is_scene_mutating,
load_server_config, new_request_id, encode_message, decode_message, etc.

Capabilities: BlenderConnection, BlenderCommandAdapter, CodeExecutionAdapter,
OperationQueue, InMemoryEventBus, MetricsCollector.

Agent: ServerOrchestrator (aggregate implementation).
Root: ServerContainer (DI wiring).
"""

# ─── Taxonomy ──────────────────────────────────────────────────

from .taxonomy_server_constant import (
    CONNECTION_STATE_CLOSED,
    CONNECTION_STATE_CONNECTED,
    CONNECTION_STATE_CONNECTING,
    CONNECTION_STATE_DISCONNECTED,
    CONNECTION_STATE_FAILED,
    CONNECTION_STATE_RECONNECTING,
    DEFAULT_COMMAND_TIMEOUT_MS,
    DEFAULT_EXECUTION_TIMEOUT_MS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL_VERSION,
    DEFAULT_QUEUE_WAIT_TIMEOUT_MS,
    DEFAULT_TASK_RETENTION_SECONDS,
    HEARTBEAT_FAILURE_THRESHOLD,
    HEARTBEAT_INTERVAL_SECONDS,
    MAX_CODE_PAYLOAD_BYTES,
    MAX_EXECUTION_OUTPUT_BYTES,
    MAX_RECONNECT_ATTEMPTS,
    MAX_COMMAND_RESPONSE_BYTES,
    OPERATION_TYPE_CODE_ASYNC,
    OPERATION_TYPE_CODE_SYNC,
    OPERATION_TYPE_COMMAND,
    QUEUE_MAX_DEPTH,
    RECONNECT_BASE_DELAY_SECONDS,
    RECONNECT_MAX_DELAY_SECONDS,
    TASK_STATE_CANCELLED,
    TASK_STATE_ERROR,
    TASK_STATE_PENDING,
    TASK_STATE_RUNNING,
    TASK_STATE_SUCCESS,
    TASK_STATE_TIMEOUT,
    TRANSPORT_SOCKET,
    TRANSPORT_STDIO,
)

from .taxonomy_server_error import (
    AdapterSurfaceError,
    AuthenticationError,
    BlenderConnectionExhausted,
    BlenderConnectionFailure,
    CommandTimeoutError,
    ConnectionClosedError,
    ConnectionConfigError,
    ExecutionError,
    ExecutionTimeoutError,
    OperationWaitTimeoutError,
    ProviderError,
    SecurityViolationError,
    ServerError,
    TaskNotFoundError,
    TooManyPendingOperationsError,
    ValidationError,
    VersionMismatchError,
)

from .taxonomy_server_vo import (
    CodeSecurityPolicy,
    CommandResult,
    ConnectionConfig,
    ConnectionState,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    ExecutionStatus,
    HeartbeatConfig,
    QueueConfig,
    QueuedOperation,
    RetryPolicy,
    ServerCommandSpec,
    ServerConfig,
    ServerMetrics,
    TaskManagerConfig,
    TaskStatus,
    TaskState,
)

from .taxonomy_server_event import (
    CodeExecuted,
    CodeExecutionFailed,
    CommandDispatched,
    CommandFailed,
    CommandTimedOut,
    ConnectionEstablished,
    ConnectionLost,
    ConnectionReconnectAttempted,
    ConnectionReconnectFailed,
    ConnectionStateChanged,
    ItemDequeued,
    ItemEnqueued,
    OperationRejected,
    SecurityViolationDetected,
    ServerEvent,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskStarted,
    TaskTimedOut,
)

# ─── Contracts ─────────────────────────────────────────────────

from .contract_server_aggregate import IBlenderServerAggregate
from .contract_connection_protocol import IBlenderConnectionProtocol
from .contract_code_execution_protocol import ICodeExecutionProtocol
from .contract_command_protocol import IBlenderCommandProtocol
from .contract_event_bus_protocol import IEventBus, IEventPublisher, IEventSubscriber
from .contract_metrics_protocol import IMetricsProvider
from .contract_operation_queue_protocol import IOperationQueueProtocol

# ─── Utility ───────────────────────────────────────────────────

from .utility_server_validator import (
    check_payload_size,
    code_fingerprint,
    validate_code_ast,
)
from .utility_server_schema import (
    effective_command_timeout_ms,
    get_command_schema,
    get_command_spec,
    is_scene_mutating,
    validate_command_args,
)
from .utility_server_config_loader import load_server_config
from .utility_server_id import new_request_id
from .utility_server_message import (
    build_command_request,
    build_handshake_request,
    build_ping_request,
    build_request,
    decode_message,
    decode_message_header,
    decode_message_payload,
    encode_message,
    parse_response,
)

# IO helpers (unchanged)
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

# Time helpers (unchanged)
from .utility_server_time import (
    calculate_deadline,
    format_duration,
    is_past_deadline,
    ms_to_seconds,
    remaining_ms,
    seconds_to_ms,
)

# String helpers (unchanged)
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
    snake_to_camel,
    starts_with_any,
    truncate_string,
)

# ─── Surface ───────────────────────────────────────────────────

from .surface_server_diagnostics_controller import ServerDiagnosticsController

# ─── __all__ ───────────────────────────────────────────────────

__all__ = [
    # Taxonomy — Constants
    "CONNECTION_STATE_CLOSED",
    "CONNECTION_STATE_CONNECTED",
    "CONNECTION_STATE_CONNECTING",
    "CONNECTION_STATE_DISCONNECTED",
    "CONNECTION_STATE_FAILED",
    "CONNECTION_STATE_RECONNECTING",
    "TASK_STATE_CANCELLED",
    "TASK_STATE_ERROR",
    "TASK_STATE_PENDING",
    "TASK_STATE_RUNNING",
    "TASK_STATE_SUCCESS",
    "TASK_STATE_TIMEOUT",
    "OPERATION_TYPE_CODE_ASYNC",
    "OPERATION_TYPE_CODE_SYNC",
    "OPERATION_TYPE_COMMAND",
    "DEFAULT_PROTOCOL_VERSION",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_EXECUTION_TIMEOUT_MS",
    "DEFAULT_COMMAND_TIMEOUT_MS",
    "MAX_CODE_PAYLOAD_BYTES",
    "MAX_EXECUTION_OUTPUT_BYTES",
    "MAX_COMMAND_RESPONSE_BYTES",
    "HEARTBEAT_INTERVAL_SECONDS",
    "HEARTBEAT_FAILURE_THRESHOLD",
    "MAX_RECONNECT_ATTEMPTS",
    "RECONNECT_BASE_DELAY_SECONDS",
    "RECONNECT_MAX_DELAY_SECONDS",
    "QUEUE_MAX_DEPTH",
    "DEFAULT_QUEUE_WAIT_TIMEOUT_MS",
    "DEFAULT_TASK_RETENTION_SECONDS",
    "TRANSPORT_SOCKET",
    "TRANSPORT_STDIO",
    # Taxonomy — VOs
    "ConnectionState",
    "ConnectionStatus",
    "ConnectionConfig",
    "ExecutionResult",
    "ExecutionErrorDetail",
    "ExecutionStatus",
    "CommandResult",
    "TaskStatus",
    "TaskState",
    "ServerMetrics",
    "ServerConfig",
    "CodeSecurityPolicy",
    "QueuedOperation",
    "ServerCommandSpec",
    "RetryPolicy",
    "HeartbeatConfig",
    "QueueConfig",
    "TaskManagerConfig",
    # Taxonomy — Events
    "ServerEvent",
    "ConnectionEstablished",
    "ConnectionLost",
    "ConnectionStateChanged",
    "ConnectionReconnectAttempted",
    "ConnectionReconnectFailed",
    "CodeExecuted",
    "CodeExecutionFailed",
    "SecurityViolationDetected",
    "TaskCreated",
    "TaskStarted",
    "TaskCompleted",
    "TaskFailed",
    "TaskTimedOut",
    "TaskCancelled",
    "CommandDispatched",
    "CommandFailed",
    "CommandTimedOut",
    "ItemEnqueued",
    "ItemDequeued",
    "OperationRejected",
    # Taxonomy — Errors
    "ServerError",
    "SecurityViolationError",
    "TooManyPendingOperationsError",
    "OperationWaitTimeoutError",
    "VersionMismatchError",
    "ConnectionConfigError",
    "AuthenticationError",
    "ConnectionClosedError",
    "BlenderConnectionExhausted",
    "BlenderConnectionFailure",
    "ExecutionTimeoutError",
    "CommandTimeoutError",
    "TaskNotFoundError",
    "ValidationError",
    "ProviderError",
    "ExecutionError",
    "AdapterSurfaceError",
    # Contracts — Aggregate
    "IBlenderServerAggregate",
    # Contracts — Protocols
    "IBlenderConnectionProtocol",
    "ICodeExecutionProtocol",
    "IBlenderCommandProtocol",
    # Contracts — Event Bus
    "IEventPublisher",
    "IEventSubscriber",
    "IEventBus",
    # Contracts — Metrics
    "IMetricsProvider",
    # Contracts — Queue
    "IOperationQueueProtocol",
    # Utility
    "validate_code_ast",
    "check_payload_size",
    "code_fingerprint",
    "validate_command_args",
    "get_command_spec",
    "is_scene_mutating",
    "effective_command_timeout_ms",
    "get_command_schema",
    "load_server_config",
    "new_request_id",
    "encode_message",
    "decode_message_header",
    "decode_message_payload",
    "build_request",
    "parse_response",
    "decode_message",
    "build_handshake_request",
    "build_ping_request",
    "build_command_request",
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
    # Surface
    "ServerDiagnosticsController",
]
