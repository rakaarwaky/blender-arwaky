"""Server domain — Value Objects for connection, execution, task state, and configuration.

Frozen dataclasses with explicit types. All VOs are immutable.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field

# ============================================================
# Connection State & Status
# ============================================================

ConnectionState = str  # "disconnected" | "connecting" | "connected" | "reconnecting" | "failed" | "closed"


@dataclass(frozen=True)
class ConnectionStatus:
    """Immutable snapshot of connection state.

    Represents the current lifecycle state of the server-to-Blender
    TCP/stdio connection with metadata for observability and
    session workspace bootstrap information.
    """

    state: ConnectionState
    host: str
    port: int
    transport_type: str = "socket"
    last_error: str | None = None
    protocol_version: str | None = None
    reconnect_attempts: int = 0
    request_id: str | None = None
    last_heartbeat_at: float | None = None
    heartbeat_interval_seconds: int = 10
    heartbeat_failure_threshold: int = 3
    session_id: str | None = None
    active_file_path: str | None = None
    active_directory: str | None = None


# ============================================================
# Execution Result
# ============================================================

ExecutionStatus = str  # "success" | "error"


@dataclass(frozen=True)
class ExecutionErrorDetail:
    """Structured error detail returned from Blender execution."""

    error_type: str
    message: str
    traceback: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class ExecutionResult:
    """Standardized result for code execution in Blender.

    Contains status, data payload, optional error detail,
    timing information, truncation flag, and request tracking ID.
    """

    status: ExecutionStatus
    data: dict | str | bytes | None = None
    error: ExecutionErrorDetail | None = None
    execution_time_ms: float = 0.0
    truncated: bool = False
    request_id: str | None = None


# ============================================================
# Command Result
# ============================================================

@dataclass(frozen=True)
class CommandResult:
    """Typed command dispatch result (replaces dict[str, Any])."""

    status: str  # "success" | "error"
    data: dict | str | None = None
    error: ExecutionErrorDetail | None = None
    execution_time_ms: float = 0.0
    truncated: bool = False
    request_id: str | None = None


# ============================================================
# Task Status
# ============================================================

TaskState = str  # "pending" | "running" | "success" | "error" | "timeout" | "cancelled"


@dataclass(frozen=True)
class TaskStatus:
    """Immutable snapshot of async task lifecycle state."""

    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    request_id: str | None = None
    created_at: float | None = None
    completed_at: float | None = None
    cancel_requested: bool = False


# ============================================================
# Server Metrics
# ============================================================

@dataclass(frozen=True)
class ServerMetrics:
    """Immutable metrics snapshot from the event bus collector."""

    pending_operations: int = 0
    running_operations: int = 0
    reconnect_count: int = 0
    failed_request_count: int = 0
    security_violation_count: int = 0
    code_execution_count: int = 0
    command_count: int = 0
    task_created_count: int = 0
    task_completed_count: int = 0
    task_failed_count: int = 0
    task_timeout_count: int = 0
    task_cancelled_count: int = 0
    average_code_latency_ms: float = 0.0
    average_command_latency_ms: float = 0.0
    last_updated_at: float = 0.0
    request_id: str | None = None


# ============================================================
# Security Policy
# ============================================================

@dataclass(frozen=True)
class CodeSecurityPolicy:
    """Static security policy for code validation."""

    allowed_directories: tuple[str, ...] = ()
    max_payload_bytes: int = 1_048_576  # 1 MB default (binary: 1k=1024)


# ============================================================
# Queued Operation
# ============================================================

@dataclass(frozen=True)
class QueuedOperation:
    """Immutable representation of an operation queued for execution."""

    request_id: str
    operation_type: str
    payload: dict
    task_id: str | None = None
    action: str | None = None
    timeout_ms: float | None = None
    enqueued_at: float = 0.0


# ============================================================
# Server Configuration
# ============================================================

@dataclass(frozen=True)
class ServerConfig:
    """Immutable server configuration resolved from file, env, and overrides."""

    # Connection
    host: str = "localhost"
    port: int = 9876
    transport_type: str = "socket"
    connection_timeout_seconds: float = 30.0
    protocol_version: str = "2.0.0"
    auth_token: str | None = None
    require_auth_for_remote: bool = True

    # Heartbeat / Reconnect
    heartbeat_interval_seconds: int = 10
    heartbeat_failure_threshold: int = 3
    reconnect_max_attempts: int = 3
    reconnect_base_delay_seconds: float = 1.0
    reconnect_max_delay_seconds: float = 4.0
    reconnect_request_policy: str = "reject"

    # Queue
    queue_max_depth: int = 50
    queue_wait_timeout_ms: float = 10_000.0

    # Execution
    execution_default_timeout_ms: float = 30_000.0
    max_code_payload_bytes: int = 1_048_576
    max_execution_output_bytes: int = 10_240

    # Commands
    command_default_timeout_ms: float = 5_000.0
    max_command_response_bytes: int = 1_048_576

    # Tasks
    task_retention_seconds: float = 600.0

    # Security
    allowed_directories: tuple[str, ...] = ()
    use_active_file_directory: bool = True

    # Workspace
    temp_blend_directory: str | None = None
    workspace_filename_prefix: str = "blender_session"
    ensure_temp_blend_file: bool = True

    # Observability
    metrics_enabled: bool = True
    event_bus_enabled: bool = True


# ============================================================
# Command Specification
# ============================================================

@dataclass(frozen=True)
class ServerCommandSpec:
    """Command metadata for catalog-driven validation and routing.

    Frozen dataclass with custom __hash__ to support set/frozenset usage.
    param_types is stored as a frozenset of tuples for hashability.
    """

    name: str
    required_params: tuple[str, ...] = ()
    optional_params: tuple[str, ...] = ()
    param_types: tuple[tuple[str, str], ...] = dc_field(default_factory=tuple)
    default_timeout_ms: float = 5_000.0
    max_timeout_ms: float = 60_000.0
    idempotent: bool = True
    mutates_scene: bool = False
    background_allowed: bool = False

    def __hash__(self) -> int:
        """Hash by name for deduplication in catalogs."""
        return hash(self.name)

    @staticmethod
    def _make_param_types(d: dict[str, str]) -> tuple[tuple[str, str], ...]:
        """Convert dict to sorted tuple of tuples for deterministic hashing."""
        return tuple(sorted(d.items()))


# ============================================================
# Connection Configuration (legacy alias — use ServerConfig)
# ============================================================

TransportType = str  # "socket" | "stdio"


@dataclass(frozen=True)
class RetryPolicy:
    """Retry configuration with exponential backoff and jitter."""

    max_retries: int
    base_delay_seconds: float
    max_delay_seconds: float


@dataclass(frozen=True)
class HeartbeatConfig:
    """Heartbeat/ping configuration for stale connection detection."""

    interval_seconds: int
    failure_threshold: int  # consecutive failures before declaring stale


@dataclass(frozen=True)
class ConnectionConfig:
    """Immutable configuration for establishing a Blender connection.

    Contains transport type, endpoint info, timeout, retry policy,
    authentication settings, protocol version, payload limits,
    heartbeat settings, and allowed directories.
    """

    transport_type: TransportType
    host: str = "localhost"
    port: int = 9876
    timeout_seconds: float = 30.0
    retry_policy: RetryPolicy | None = None
    auth_token: str | None = None
    protocol_version: str | None = None
    heartbeat: HeartbeatConfig | None = None
    max_payload_bytes: int = 1_048_576  # 1 MB default (binary: 1k=1024)
    allowed_directories: list[str] = dc_field(default_factory=list)


# ============================================================
# Queue Configuration
# ============================================================


@dataclass(frozen=True)
class QueueConfig:
    """Immutable configuration for execution queue parameters."""

    max_depth: int = 50
    wait_timeout_ms: float = 10_000.0  # 10 seconds default


# ============================================================
# Task Manager Configuration
# ============================================================


@dataclass(frozen=True)
class TaskManagerConfig:
    """Immutable configuration for task manager parameters."""

    retention_seconds: float = 600.0  # 10 minutes default
