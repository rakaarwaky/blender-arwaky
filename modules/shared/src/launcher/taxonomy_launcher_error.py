"""Launcher domain — Error types for process lifecycle operations.

All errors subclass LauncherError with explicit error codes.
"""

from __future__ import annotations


class LauncherError(Exception):
    """Base error for all launcher-domain exceptions."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "details": self.details}


# ─── Process Not Running ───────────────────────────────────

class BlenderNotRunningError(LauncherError):
    """Raised when an operation expects a Blender process that is absent."""

    def __init__(self, message: str = "Blender process not running", details: dict | None = None) -> None:
        super().__init__("blender_not_running", message, details)


# ─── State Errors ──────────────────────────────────────────

class StateError(LauncherError):
    """Raised for invalid, corrupt, or conflicting runtime state."""

    def __init__(self, message: str = "Invalid runtime state", details: dict | None = None) -> None:
        super().__init__("state_error", message, details)


# ─── Configuration Errors ──────────────────────────────────

class LauncherConfigError(LauncherError):
    """Raised when Blender path is not configured, locatable, or invalid."""

    def __init__(self, message: str = "Launcher configuration error", details: dict | None = None) -> None:
        super().__init__("configuration_error", message, details)


# ─── Timeout Errors ────────────────────────────────────────

class LaunchTimeoutError(LauncherError):
    """Raised when readiness is not confirmed within launch timeout."""

    def __init__(self, message: str = "Launch readiness timeout", details: dict | None = None) -> None:
        super().__init__("launch_timeout", message, details)


class ShutdownTimeoutError(LauncherError):
    """Raised when graceful shutdown exceeds timeout and force is disallowed."""

    def __init__(self, message: str = "Shutdown timeout", details: dict | None = None) -> None:
        super().__init__("shutdown_timeout", message, details)


# ─── Launch / Spawn Errors ─────────────────────────────────

class LaunchError(LauncherError):
    """Raised when the process cannot be spawned or exits during startup."""

    def __init__(self, message: str = "Launch failed", details: dict | None = None) -> None:
        super().__init__("launch_error", message, details)


# ─── Validation Errors ─────────────────────────────────────

class ExecutableValidationError(LauncherError):
    """Raised when a candidate executable fails authenticity/permission/version checks."""

    def __init__(self, message: str = "Executable validation failed", details: dict | None = None) -> None:
        super().__init__("validation_error", message, details)


# ─── Termination Errors ────────────────────────────────────

class TerminationError(LauncherError):
    """Raised when force termination is attempted but the process cannot be stopped."""

    def __init__(self, message: str = "Termination failed", details: dict | None = None) -> None:
        super().__init__("termination_error", message, details)
