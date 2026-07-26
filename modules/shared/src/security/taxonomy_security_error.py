"""Security domain — Error types for path, archive, code, redaction, and audit failures.

All errors subclass SecurityError with explicit error codes.
"""

from __future__ import annotations


class SecurityError(Exception):
    """Base error for all security-domain exceptions."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Path Validation Errors ─────────────────────────────────────


class PathTraversalError(SecurityError):
    """Raised when a path traversal attempt is detected."""

    def __init__(self, path: str = "", details: dict | None = None) -> None:
        super().__init__(
            "path_traversal",
            f"Path traversal detected: {path}",
            {"path": path, **(details or {})},
        )


class UnauthorizedAccessError(SecurityError):
    """Raised when a path is outside allowed directories."""

    def __init__(self, path: str = "", details: dict | None = None) -> None:
        super().__init__(
            "unauthorized_access",
            f"Access denied: {path}",
            {"path": path, **(details or {})},
        )


class SymlinkEscapeError(SecurityError):
    """Raised when a symbolic link escapes allowed directories."""

    def __init__(self, path: str = "", details: dict | None = None) -> None:
        super().__init__(
            "symlink_escape",
            f"Symbolic link escape: {path}",
            {"path": path, **(details or {})},
        )


# ─── Archive Safety Errors ──────────────────────────────────────


class ArchiveSafetyError(SecurityError):
    """Raised when archive extraction violates safety policy."""

    def __init__(self, message: str = "Archive safety violation", details: dict | None = None) -> None:
        super().__init__("archive_safety", message, details)


class ArchiveBombError(SecurityError):
    """Raised when an archive bomb pattern is detected."""

    def __init__(self, message: str = "Archive bomb detected", details: dict | None = None) -> None:
        super().__init__("archive_bomb", message, details)


# ─── Code Validation Errors ─────────────────────────────────────


class CodeValidationError(SecurityError):
    """Raised when untrusted code fails validation."""

    def __init__(self, message: str = "Code validation failed", details: dict | None = None) -> None:
        super().__init__("code_validation", message, details)


class CodeOversizedError(SecurityError):
    """Raised when code exceeds maximum allowed size."""

    def __init__(self, size: int = 0, max_size: int = 0, details: dict | None = None) -> None:
        super().__init__(
            "code_oversized",
            f"Code payload too large: {size} bytes (max: {max_size})",
            {"size": size, "max_size": max_size, **(details or {})},
        )


# ─── Redaction Errors ───────────────────────────────────────────


class RedactionError(SecurityError):
    """Raised when sensitive value redaction fails."""

    def __init__(self, message: str = "Redaction failed", details: dict | None = None) -> None:
        super().__init__("redaction_error", message, details)


# ─── Audit Errors ───────────────────────────────────────────────


class AuditEmissionError(SecurityError):
    """Raised when audit event delivery fails."""

    def __init__(self, message: str = "Audit emission failed", details: dict | None = None) -> None:
        super().__init__("audit_emission", message, details)


# ─── Policy Errors ──────────────────────────────────────────────


class ValidationError(SecurityError):
    """Raised for malformed request or invalid security policy input."""

    def __init__(self, message: str = "Validation error", details: dict | None = None) -> None:
        super().__init__("validation_error", message, details)
