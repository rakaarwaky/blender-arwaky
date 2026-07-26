"""Server domain — Typed error types for connection, execution, queue, and task lifecycle.

All errors subclass ServerError with explicit error codes for MCP serialization.
No bare string errors in public API.
"""

from __future__ import annotations


class ServerError(Exception):
    """Base error for all server-domain exceptions.

    Provides structured error info with code/message/details for
    MCP error serialization and observability.
    """

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}  # type: ignore[dict-item]
        super().__init__(f"[{code}] {message}")

    def to_mcp_format(self) -> dict:  # noqa: ANN004
        """Serialize error for MCP response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Security Errors ──────────────────────────────────────────────


class SecurityViolationError(ServerError):
    """Raised when user-provided code contains blocked patterns or violates sandbox policy."""

    def __init__(self, message: str = "Security violation", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("security_violation", message, details)


# ─── Execution Errors ──────────────────────────────────────────────


class CodeValidationError(ServerError):
    """Raised when code fails static analysis or contains blocked patterns."""

    def __init__(self, message: str = "Code validation failed", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("code_validation_error", message, details)


class ExecutionTimeoutError(ServerError):
    """Raised when code execution exceeds the configured timeout."""

    def __init__(self, timeout_ms: float = 30_000.0, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("execution_timeout", f"Execution exceeded {timeout_ms}ms", {"timeout_ms": timeout_ms})


class CommandTimeoutError(ServerError):
    """Raised when a command response exceeds the configured timeout."""

    def __init__(self, action: str = "", timeout_ms: float = 5_000.0, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("command_timeout", f"Command '{action}' timed out after {timeout_ms}ms", {"action": action, "timeout_ms": timeout_ms})


# ─── Queue Errors ────────────────────────────────────────────────


class QueueFullError(ServerError):
    """Raised when the serialized execution queue has reached maximum depth."""

    def __init__(self, max_depth: int = 50, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("queue_full", f"Queue full (depth={max_depth})", {"max_depth": max_depth})


class QueueTimeoutError(ServerError):
    """Raised when a queued operation exceeds the configured wait timeout."""

    def __init__(self, request_id: str = "", timeout_ms: float = 10_000.0, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("queue_timeout", f"Queue wait timeout for {request_id}", {"request_id": request_id, "timeout_ms": timeout_ms})


# ─── Task Errors ────────────────────────────────────────────────


class TaskNotFoundError(ServerError):
    """Raised when polling an unknown or expired async task."""

    def __init__(self, task_id: str = "", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("task_not_found", f"Task not found: {task_id}", {"task_id": task_id})


# ─── Connection Errors ──────────────────────────────────────────


class ConnectionConfigError(ServerError):
    """Raised when connection factory receives invalid configuration."""

    def __init__(self, message: str = "Connection config error", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_config_error", message, details)


class AuthenticationError(ServerError):
    """Raised when connection authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("authentication_failed", message, details)


class ProtocolVersionMismatchError(ServerError):
    """Raised when server and Blender addon protocol versions are incompatible."""

    def __init__(self, expected: str = "", actual: str = "", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("protocol_version_mismatch", f"Expected {expected}, got {actual}", {"expected": expected, "actual": actual})


class ConnectionClosedError(ServerError):
    """Raised when an operation is rejected after graceful disconnect."""

    def __init__(self, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_closed", "Connection already closed", details)


class BlenderConnectionExhausted(ServerError):
    """Raised after all reconnect attempts have been exhausted."""

    def __init__(self, attempts: int = 3, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_retries_exhausted", f"All {attempts} reconnect attempts failed", {"attempts": attempts})


# ─── Adapter / Surface Errors ────────────────────────────────────


class AdapterSurfaceError(ServerError):
    """Raised when an unexpected adapter surface failure occurs."""

    def __init__(self, message: str = "Adapter surface error", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("adapter_surface_error", message, details)
