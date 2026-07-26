"""Gateway domain — Value Objects for connection, transport, queue, and execution.

Frozen dataclasses with explicit types. All VOs are immutable.
Input and output fields live in a single VO per concept.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from enum import Enum


# ============================================================
# Connection State / Transport
# ============================================================

class ConnectionState(str, Enum):
    """Connection state machine states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    CLOSED = "closed"


class TransportType(str, Enum):
    """Transport channel type."""

    LOCAL_SOCKET = "local_socket"
    STDIO_PIPE = "stdio_pipe"


# ============================================================
# FR-GWY-001: Establish Connection
# ============================================================

@dataclass(frozen=True)
class ConnectionRequestVO:
    """Unified connection request — input and output in one VO."""

    host: str = "localhost"
    port: int = 50051
    transport_type: TransportType = TransportType.LOCAL_SOCKET
    timeout_seconds: float = 30.0
    protocol_version: str = "1.0"
    auth_enabled: bool = False
    auth_material: str | None = None


@dataclass(frozen=True)
class ConnectionResultVO:
    """Unified connection result — input and output in one VO."""

    state: ConnectionState = ConnectionState.DISCONNECTED
    protocol_version: str = ""
    transport_type: TransportType = TransportType.LOCAL_SOCKET
    endpoint_summary: str = ""
    capabilities: tuple[str, ...] = dc_field(default_factory=tuple)
    error: str | None = None


# ============================================================
# FR-GWY-002: Maintain Connection
# ============================================================

@dataclass(frozen=True)
class ConnectionStatusVO:
    """Unified connection status — input and output in one VO."""

    state: ConnectionState = ConnectionState.DISCONNECTED
    last_heartbeat_timestamp: float | None = None
    reconnect_attempts: int = 0
    last_failure_reason: str | None = None
    active_operation_in_progress: bool = False


# ============================================================
# FR-GWY-003: Transport Request and Response
# ============================================================

@dataclass(frozen=True)
class TransportRequestVO:
    """Unified transport request — input and output in one VO."""

    operation_class: str = ""
    payload: bytes | None = None
    timeout_override_seconds: float | None = None
    tracking_id: str = ""


@dataclass(frozen=True)
class TransportResponseVO:
    """Unified transport response — input and output in one VO."""

    tracking_id: str = ""
    status: str = "pending"  # success | error
    payload: bytes | None = None
    duration_ms: float = 0.0
    request_size_bytes: int = 0
    response_size_bytes: int = 0
    error: str | None = None


# ============================================================
# FR-GWY-004: Scene Operation Queue
# ============================================================

@dataclass(frozen=True)
class SceneOperationVO:
    """Unified scene operation request — input and output in one VO."""

    is_mutation: bool = False
    payload: bytes | None = None
    priority: int = 0


@dataclass(frozen=True)
class SceneOperationResultVO:
    """Unified scene operation result — input and output in one VO."""

    status: str = "pending"  # success | error | rejected | timeout
    queue_wait_ms: float = 0.0
    execution_duration_ms: float = 0.0
    payload: bytes | None = None
    error: str | None = None


@dataclass(frozen=True)
class QueueStatusVO:
    """Unified queue status — input and output in one VO."""

    current_depth: int = 0
    is_busy: bool = False
    max_depth: int = 50


# ============================================================
# FR-GWY-005: Execute Raw Python Code
# ============================================================

@dataclass(frozen=True)
class CodeExecutionRequestVO:
    """Unified code execution request — input and output in one VO."""

    code: str = ""
    timeout_override_seconds: float | None = None
    tracking_id: str = ""
    as_background_task: bool = False


@dataclass(frozen=True)
class CodeExecutionResultVO:
    """Unified code execution result — input and output in one VO."""

    status: str = "pending"  # success | error | timeout | security_violation
    output: str = ""
    truncated: bool = False
    duration_ms: float = 0.0
    error_category: str | None = None
    error_message: str | None = None
    error_location: str | None = None
    task_reference: str | None = None
