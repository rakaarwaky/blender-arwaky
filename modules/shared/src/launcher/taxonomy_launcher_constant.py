"""Launcher domain — Constants for discovery order, defaults, and events."""

from __future__ import annotations

# ─── Discovery Order (FR-LAU-001 deterministic) ─────────────

LAUNCHER_DISCOVERY_ORDER: tuple[str, ...] = (
    "override",
    "configured",
    "environment",
    "platform",
    "system_path",
)

# ─── Default Limits ─────────────────────────────────────────

LAUNCHER_DEFAULT_LAUNCH_TIMEOUT_SECONDS: float = 30.0
LAUNCHER_DEFAULT_SHUTDOWN_TIMEOUT_SECONDS: float = 10.0
LAUNCHER_DEFAULT_READINESS_PROBE_INTERVAL_SECONDS: float = 0.5

# ─── Launch Modes ────────────────────────────────────────────

LAUNCHER_MODE_INTERFACE: str = "interface"
LAUNCHER_MODE_HEADLESS: str = "headless"

# ─── Termination Methods ────────────────────────────────────

LAUNCHER_TERMINATION_GRACEFUL: str = "graceful"
LAUNCHER_TERMINATION_FORCE: str = "force"
LAUNCHER_TERMINATION_NONE: str = "none"

# ─── Secret Key Detection ────────────────────────────────────

SECRET_KEYS: tuple[str, ...] = ("secret", "token", "password", "credential", "auth")

# ─── Event Categories ───────────────────────────────────────

LAUNCHER_EVENT_APPLICATION_STARTED: str = "application_started"
LAUNCHER_EVENT_LAUNCH_FAILED: str = "application_launch_failed"
LAUNCHER_EVENT_APPLICATION_STOPPED: str = "application_stopped"
LAUNCHER_EVENT_SHUTDOWN_ESCALATION: str = "shutdown_escalation"
LAUNCHER_EVENT_STATUS_CHECKED: str = "runtime_status_checked"
LAUNCHER_EVENT_STALE_STATE_DETECTED: str = "stale_state_detected"
LAUNCHER_EVENT_EXECUTABLE_REGISTERED: str = "executable_registered"
LAUNCHER_EVENT_CORRUPT_STATE_DETECTED: str = "corrupt_state_detected"

# ─── Source Feature Name ────────────────────────────────────
# REMOVED: LAUNCHER_SOURCE_FEATURE is unused.

# If needed in the future, document its intended use before re-adding.
