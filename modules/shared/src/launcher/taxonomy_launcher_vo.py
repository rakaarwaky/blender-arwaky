"""Launcher domain — Value Objects for executable registration, launch,
shutdown, runtime status, and state persistence.

Frozen dataclasses with explicit types. All VOs are immutable.
Input and output fields live in a single VO per concept.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum
from typing import NewType

TimeoutSeconds = NewType("TimeoutSeconds", float)

# ============================================================
# Shared Taxonomy Enums (replaces primitive str types)
# ============================================================


class LaunchMode(str, Enum):
    """Launch mode preference."""

    INTERFACE = "interface"
    HEADLESS = "headless"


class ProbeDepth(str, Enum):
    """Probe depth preference for status checks."""

    LIGHTWEIGHT = "lightweight"
    FULL = "full"


class TerminationMethod(str, Enum):
    """Termination method used during shutdown."""

    GRACEFUL = "graceful"
    FORCE = "force"
    NONE = "none"


class LaunchMethod(str, Enum):
    """How the launch was performed."""

    SPAWN = "spawn"
    IDEMPOTENT = "idempotent"


# ============================================================
# Registration Source / Discovery
# ============================================================

class RegistrationSource(str, Enum):
    """How the Blender executable path was discovered."""

    OVERRIDE = "override"
    CONFIGURED = "configured"
    ENVIRONMENT = "environment"
    PLATFORM = "platform"
    SYSTEM_PATH = "system_path"


class VersionCompatibility(str, Enum):
    """Version compatibility verdict."""

    SUPPORTED = "supported"
    WARNING = "warning"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


# ============================================================
# Runtime State Classification (FR-LAU-004)
# ============================================================

class RuntimeState(str, Enum):
    """Classified runtime state."""

    NOT_RUNNING = "not_running"
    STARTING = "starting"
    RUNNING_READY = "running_ready"
    RUNNING_UNRESPONSIVE = "running_unresponsive"
    STOPPING = "stopping"
    STALE = "stale"


# ============================================================
# FR-LAU-001: Locate and Register
# ============================================================

@dataclass(frozen=True)
class ExecutableReferenceVO:
    """Validated Blender executable reference."""

    path: str
    version_summary: str = ""
    compatibility: VersionCompatibility = VersionCompatibility.UNKNOWN


@dataclass(frozen=True)
class RegistrationOutcomeVO:
    """Unified registration result — input and output in one VO."""

    executable: ExecutableReferenceVO | None = None
    source: RegistrationSource = RegistrationSource.SYSTEM_PATH
    registered: bool = False
    warning: str | None = None
    error: str | None = None


# ============================================================
# FR-LAU-002: Launch
# ============================================================

@dataclass(frozen=True)
class LaunchOutcomeVO:
    """Unified launch result — input and output in one VO."""

    success: bool = False
    process_id: int | None = None
    ready: bool = False
    bridge_endpoint: str | None = None
    duration_ms: float = 0.0
    launch_method: LaunchMethod = LaunchMethod.SPAWN
    error: str | None = None


# ============================================================
# FR-LAU-003: Shut Down
# ============================================================

@dataclass(frozen=True)
class ShutdownOutcomeVO:
    """Unified shutdown result — input and output in one VO."""

    success: bool = False
    termination_method: TerminationMethod = TerminationMethod.NONE
    duration_ms: float = 0.0
    final_state: RuntimeState = RuntimeState.NOT_RUNNING
    escalated: bool = False
    error: str | None = None


# ============================================================
# FR-LAU-004: Runtime Status
# ============================================================

@dataclass(frozen=True)
class RuntimeStatusVO:
    """Unified runtime status — input and output in one VO."""

    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    ready: bool = False
    stale: bool = False
    uptime_seconds: float | None = None
    depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT


@dataclass(frozen=True)
class StatusCheckOutcomeVO:
    """Unified runtime status check result — input and output in one VO."""

    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    bridge_endpoint: str | None = None
    duration_ms: float = 0.0
    error: str | None = None


# ============================================================
# FR-LAU-005: Persist Runtime State
# ============================================================

@dataclass(frozen=True)
class RuntimeStateVO:
    """Persisted runtime state record."""

    executable_path: str = ""
    process_id: int | None = None
    launch_timestamp: float = 0.0
    bridge_endpoint: str | None = None
    last_status: RuntimeState = RuntimeState.NOT_RUNNING

    def contains_secret(self) -> bool:
        from dataclasses import fields

        from .taxonomy_launcher_constant import SECRET_KEYS

        field_names = {f.name for f in fields(self)}
        for key in SECRET_KEYS:
            if key in field_names:
                return True
        return False


@dataclass(frozen=True)
class PersistenceOutcomeVO:
    """Unified persistence result — input and output in one VO."""

    success: bool = False
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    reconciled: bool = False


@dataclass(frozen=True)
class LoadOutcomeVO:
    """FR-LAU-005 (Finding #14): Load result with corruption differentiation.

    Differentiates between corrupt/unreadable content and missing/empty state file.
    Returns the loaded state when available, plus warnings for corruption events.
    """

    state: RuntimeStateVO | None = None
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    corrupted: bool = False


@dataclass(frozen=True)
class StatePersistenceOutcomeVO:
    """Unified state persistence result — input and output in one VO."""

    success: bool = False
    duration_ms: float = 0.0
    error: str | None = None


# ============================================================
# Launcher Configuration
# ============================================================

@dataclass(frozen=True)
class LauncherConfigVO:
    """Launcher configuration resolved from config feature / environment."""

    executable_path: str | None = None
    search_locations: tuple[str, ...] = dc_field(default_factory=tuple)
    supported_version_range: str = ""
    launch_timeout_seconds: float = 30.0
    shutdown_timeout_seconds: float = 10.0
    force_termination_enabled: bool = True
    readiness_probe_interval_seconds: float = 0.5
    state_persistence_location: str | None = None
    default_launch_mode: LaunchMode = LaunchMode.INTERFACE
    stale_reconciliation_enabled: bool = True
