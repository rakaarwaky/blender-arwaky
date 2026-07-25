"""Server domain — Error types for connection, execution, queue, and security violations."""

from __future__ import annotations

from ..common.taxonomy_core_vo import Details, ErrorString


class ServerError(Exception):
    """Base error for all server-domain exceptions."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("Server error")
        super().__init__(message)
        self.details = details or {}
        self._error_message: ErrorString = ErrorString(str(message))

    def to_mcp_format(self) -> dict[str, Any]:  # noqa: ANN401
        """Serialize error for MCP response."""
        return {
            "code": self.__class__.__name__,
            "message": str(ErrorString(str(self))),
            "details": getattr(self, "details", None),
        }


# ─── Security Errors ──────────────────────────────────────────────────────────


class SecurityViolationError(ServerError):
    """Raised when user-provided code contains blocked patterns or violates sandbox policy."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Security violation"), details)


# ─── Execution Errors ────────────────────────────────────────────────────────


class ExecutionTimeoutError(ServerError):
    """Raised when code execution exceeds the configured timeout."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Execution timeout"), details)


class CommandTimeoutError(ServerError):
    """Raised when a command response exceeds the configured timeout."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Command timeout"), details)


# ─── Queue Errors ────────────────────────────────────────────────────────────


class QueueFullError(ServerError):
    """Raised when the serialized execution queue has reached maximum depth."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Execution queue full"), details)


class QueueTimeoutError(ServerError):
    """Raised when a queued operation exceeds the configured wait timeout."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Queue wait timeout"), details)


# ─── Task Errors ─────────────────────────────────────────────────────────────


class TaskNotFoundError(ServerError):
    """Raised when polling an unknown or expired async task."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Task not found"), details)


# ─── Connection Errors ──────────────────────────────────────────────────────


class ConnectionConfigError(ServerError):
    """Raised when connection factory receives invalid configuration."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Connection config error"), details)


class AuthenticationError(ServerError):
    """Raised when connection authentication fails."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Authentication failed"), details)


class ProtocolVersionMismatchError(ServerError):
    """Raised when server and Blender addon protocol versions are incompatible."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Protocol version mismatch"), details)


class ConnectionClosedError(ServerError):
    """Raised when an operation is rejected after graceful disconnect."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Connection closed"), details)


class BlenderConnectionExhausted(ServerError):
    """Raised after all reconnect attempts have been exhausted."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("All connection retries exhausted"), details)


# ─── Adapter / Surface Errors ────────────────────────────────────────────────


class AdapterSurfaceError(ServerError):
    """Raised when an unexpected adapter surface failure occurs."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        super().__init__(message or ErrorString("Adapter surface error"), details)
