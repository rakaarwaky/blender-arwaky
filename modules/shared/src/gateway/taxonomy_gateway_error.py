"""Taxonomy error types for gateway and server domains.

Gateway errors (lines 8-56): simple exceptions for transport/connection failures.
Server errors (lines 57+): MCP-serializable errors with code/message/details.
All errors use explicit typed classes — no bare strings.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    Details,
    DurationMs,
    ErrorMessage,
    ErrorString,
    QueueDepth,
    ReconnectAttempt,
    RequestId,
    TaskUuid,
    VersionString,
)

# VO singleton defaults (B008-safe: no constructor calls in argument defaults)
DEFAULT_SECURITY_MSG: ErrorString = ErrorString("Security violation")
DEFAULT_EXEC_TIMEOUT_MS: DurationMs = DurationMs(30_000.0)
DEFAULT_ACTION_REF: ActionName = ActionName("")
DEFAULT_CMD_TIMEOUT_MS: DurationMs = DurationMs(5_000.0)
DEFAULT_QUEUE_DEPTH: QueueDepth = QueueDepth(50)
DEFAULT_REQUEST_REF: RequestId = RequestId("")
DEFAULT_OP_TIMEOUT_MS: DurationMs = DurationMs(10_000.0)
DEFAULT_TASK_REF: TaskUuid = TaskUuid("")
DEFAULT_CONFIG_ERR_MSG: ErrorString = ErrorString("Connection config error")
DEFAULT_AUTH_ERR_MSG: ErrorString = ErrorString("Authentication failed")
DEFAULT_VERSION_REF: VersionString = VersionString("")
DEFAULT_RECONNECT_ATTEMPTS: ReconnectAttempt = ReconnectAttempt(3)
DEFAULT_BLENDER_CONN_MSG: ErrorString = ErrorString("Blender connection failure")
DEFAULT_VALIDATION_MSG: ErrorString = ErrorString("Validation error")
DEFAULT_VALIDATION_CODE: ErrorString = ErrorString("validation_error")
DEFAULT_PROVIDER_MSG: ErrorString = ErrorString("Provider error")
DEFAULT_EXECUTION_MSG: ErrorString = ErrorString("Execution error")
DEFAULT_ADAPTER_MSG: ErrorString = ErrorString("Adapter surface error")


class GatewayError(Exception):
    """Base error for all gateway domain exceptions."""


class ConnectionError(GatewayError):
    """Connection failed, refused, or lost."""


class TimeoutError(GatewayError):
    """Transport timeout, execution timeout, or queue wait timeout exceeded."""


class ProtocolVersionMismatchError(GatewayError):
    """Protocol version incompatible between application and Blender bridge."""


class ChannelConflictError(GatewayError):
    """Queue conflict, queue depth limit reached, or serialization contention."""


class TransportParseError(GatewayError):
    """Malformed frame or unparseable response content."""


class PayloadLimitError(GatewayError):
    """Request or response exceeded configured payload size."""


class ServerError(Exception):
    """Base error for all server-domain exceptions.

    Provides structured error info with code/message/details for
    MCP error serialization and observability.
    """

    def __init__(self, code: ErrorString, message: ErrorMessage, _details: Details | None = None) -> None:
        self.code = code
        self.message = message
        self.details = dict(_details) if _details else {}
        super().__init__(f"[{code}] {message}")

    def to_mcp_format(self) -> dict[str, object]:
        """Serialize error for MCP response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Security Errors ──────────────────────────────────────────────


class SecurityViolationError(ServerError):
    """Raised when user-provided code contains blocked patterns or violates sandbox policy.

    Single source of truth for security violation errors across features.
    Gateway delegates code validation to security feature; this error is
    raised when the validation result indicates a violation.
    """

    def __init__(self, message: ErrorString = DEFAULT_SECURITY_MSG, _details: Details | None = None) -> None:
        super().__init__("security_violation", message, _details)


# ─── Execution Errors ──────────────────────────────────────────────


class ExecutionTimeoutError(ServerError):
    """Raised when code execution exceeds the configured timeout."""

    def __init__(self, timeout_ms: DurationMs = DEFAULT_EXEC_TIMEOUT_MS, _details: Details | None = None) -> None:
        super().__init__("execution_timeout", f"Execution exceeded {timeout_ms}ms", {"timeout_ms": timeout_ms})


class CommandTimeoutError(ServerError):
    """Raised when a command response exceeds the configured timeout."""

    def __init__(
        self,
        action: ActionName = DEFAULT_ACTION_REF,
        timeout_ms: DurationMs = DEFAULT_CMD_TIMEOUT_MS,
        _details: Details | None = None,
    ) -> None:
        super().__init__(
            "command_timeout",
            f"Command '{action}' timed out after {timeout_ms}ms",
            {"action": action, "timeout_ms": timeout_ms},
        )


# ─── Queue Errors (renamed v2.0.0) ──────────────────────────────


class PendingOpsLimitError(ServerError):
    """Raised when the serialized execution queue has reached maximum depth.

    Error code: 'too_many_pending_operations'
    """

    def __init__(
        self,
        max_depth: QueueDepth = DEFAULT_QUEUE_DEPTH,
        request_id: RequestId | None = None,
        _details: Details | None = None,
    ) -> None:
        super().__init__(
            "too_many_pending_operations",
            f"Queue full (depth={max_depth})",
            {"max_depth": max_depth, "request_id": request_id, **(_details or {})},
        )


# Backward compatibility alias
TooManyPendingOperationsError = PendingOpsLimitError


class OperationWaitTimeoutError(ServerError):
    """Raised when a queued operation exceeds the configured wait timeout.

    Renamed from QueueTimeoutError in v2.0.0.
    Error code: 'operation_wait_timeout'
    """

    def __init__(
        self,
        request_id: RequestId = DEFAULT_REQUEST_REF,
        timeout_ms: DurationMs = DEFAULT_OP_TIMEOUT_MS,
        _details: Details | None = None,
    ) -> None:
        super().__init__(
            "operation_wait_timeout",
            f"Operation wait timeout for {request_id}",
            {"request_id": request_id, "timeout_ms": timeout_ms},
        )


# ─── Task Errors ────────────────────────────────────────────────


class TaskNotFoundError(ServerError):
    """Raised when polling an unknown or expired async task."""

    def __init__(self, task_id: TaskUuid = DEFAULT_TASK_REF, _details: Details | None = None) -> None:
        super().__init__("task_not_found", f"Task not found: {task_id}", {"task_id": task_id})


# ─── Connection Errors ──────────────────────────────────────────


class ConnectionConfigError(ServerError):
    """Raised when connection factory receives invalid configuration."""

    def __init__(self, message: ErrorString = DEFAULT_CONFIG_ERR_MSG, _details: Details | None = None) -> None:
        super().__init__("connection_config_error", message, _details)


class AuthenticationError(ServerError):
    """Raised when connection authentication fails."""

    def __init__(self, message: ErrorString = DEFAULT_AUTH_ERR_MSG, _details: Details | None = None) -> None:
        super().__init__("authentication_failed", message, _details)


class VersionMismatchError(ServerError):
    """Raised when server and Blender addon protocol versions are incompatible.

    Renamed from ProtocolVersionMismatchError in v2.0.0.
    Error code: 'version_mismatch'
    """

    def __init__(
        self,
        expected: VersionString = DEFAULT_VERSION_REF,
        actual: VersionString = DEFAULT_VERSION_REF,
        _details: Details | None = None,
    ) -> None:
        super().__init__(
            "version_mismatch",
            f"Expected major version {expected}, got {actual}",
            {"expected": expected, "actual": actual},
        )


class ConnectionClosedError(ServerError):
    """Raised when an operation is rejected after graceful disconnect."""

    def __init__(self, _details: Details | None = None) -> None:
        super().__init__("connection_closed", "Connection already closed", _details)


class BlenderConnectionExhausted(ServerError):  # noqa: N818 - public taxonomy name
    """Raised after all reconnect attempts have been exhausted."""

    def __init__(
        self, attempts: ReconnectAttempt = DEFAULT_RECONNECT_ATTEMPTS, _details: Details | None = None
    ) -> None:
        super().__init__(
            "connection_retries_exhausted", f"All {attempts} reconnect attempts failed", {"attempts": attempts}
        )


class BlenderConnectionFailure(ServerError):  # noqa: N818 - public taxonomy name
    """Raised when connection is lost or unavailable."""

    def __init__(self, message: ErrorString = DEFAULT_BLENDER_CONN_MSG, _details: Details | None = None) -> None:
        super().__init__("blender_connection_failure", message, _details)


# ─── Validation Errors ──────────────────────────────────────────


class GatewayValidationError(ServerError):
    """Raised for unknown commands, invalid parameters, or syntax errors."""

    def __init__(
        self,
        message: ErrorString = DEFAULT_VALIDATION_MSG,
        code: ErrorString = DEFAULT_VALIDATION_CODE,
        details: Details | None = None,
    ) -> None:
        super().__init__(code, message, details)


# ─── Adapter / Surface Errors ────────────────────────────────────


class GatewayProviderError(ServerError):
    """Raised when Blender addon returns a command-specific failure."""

    def __init__(self, message: ErrorString = DEFAULT_PROVIDER_MSG, _details: Details | None = None) -> None:
        super().__init__("provider_error", message, _details)


class GatewayExecutionError(ServerError):
    """Raised when Blender code execution returns a runtime failure."""

    def __init__(self, message: ErrorString = DEFAULT_EXECUTION_MSG, _details: Details | None = None) -> None:
        super().__init__("execution_error", message, _details)


class AdapterSurfaceError(ServerError):
    """Raised when an unexpected adapter surface failure occurs."""

    def __init__(self, message: ErrorString = DEFAULT_ADAPTER_MSG, _details: Details | None = None) -> None:
        super().__init__("adapter_surface_error", message, _details)


# ─── Backward-compatible aliases ────────────────────────────────

ProviderError = GatewayProviderError
ValidationError = GatewayValidationError
