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

DurationMs = NewType("DurationMs", float)
TimeoutSeconds = NewType("TimeoutSeconds", float)

# ============================================================
# FRD Error Categories (machine-readable)
# ============================================================


class LauncherErrorCode(str, Enum):
    """FRD error categories mapped to machine-readable codes."""

    BLENDER_NOT_RUNNING = "blender_not_running"
    STATE_ERROR = "state_error"
    CONFIGURATION_ERROR = "configuration_error"
    TIMEOUT_ERROR = "timeout_error"
    LAUNCH_ERROR = "launch_error"
    VALIDATION_ERROR = "validation_error"
    TERMINATION_ERROR = "termination_error"


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
    source: RegistrationSource | None = None
    registered: bool = False
    warning: str | None = None
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


# ============================================================
# FR-LAU-002: Launch Request / Bridge Endpoint Settings
# ============================================================


@dataclass(frozen=True)
class BridgeEndpointSettingsVO:
    """Bridge endpoint settings for launcher integration."""

    host: str
    port: int
    protocol_version: str | None = None


@dataclass(frozen=True)
class LaunchRequestVO:
    """FR-LAU-002 launch input with bridge endpoint settings."""

    mode: LaunchMode = LaunchMode.INTERFACE
    readiness_timeout: TimeoutSeconds | None = None
    bridge_endpoint: BridgeEndpointSettingsVO | None = None


# ============================================================
# FR-LAU-003: Shutdown Request
# ============================================================


@dataclass(frozen=True)
class ShutdownRequestVO:
    """FR-LAU-003 shutdown input with explicit force/escalation semantics."""

    force_requested: bool = False
    escalation_confirmed: bool = True


# ============================================================
# FR-LAU-002: Launch Outcome
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
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


# ============================================================
# FR-LAU-003: Shut Down Outcome
# ============================================================


@dataclass(frozen=True)
class ShutdownOutcomeVO:
    """Unified shutdown result — input and output in one VO."""

    success: bool = False
    termination_method: TerminationMethod = TerminationMethod.NONE
    duration_ms: float = 0.0
    final_state: RuntimeState = RuntimeState.NOT_RUNNING
    escalated: bool = False
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


# ============================================================
# FR-LAU-004: Runtime Status
# ============================================================


@dataclass(frozen=True)
class RuntimeStatusVO:
    """Unified runtime status — input and output in one VO.

    Includes diagnostics-friendly metadata (process reference,
    bridge endpoint summary, probe duration, classification reason).
    Secrets are redacted.
    """

    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    process_reference: str = ""
    bridge_endpoint_summary: str | None = None
    ready: bool = False
    stale: bool = False
    uptime_seconds: float | None = None
    probe_duration_ms: float = 0.0
    depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT


@dataclass(frozen=True)
class StatusCheckOutcomeVO:
    """Unified runtime status check result — input and output in one VO."""

    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    bridge_endpoint: str | None = None
    duration_ms: float = 0.0
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


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


@dataclass(frozen=True)
class PersistenceOutcomeVO:
    """Unified persistence result — input and output in one VO."""

    success: bool = False
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    reconciled: bool = False


@dataclass(frozen=True)
class StatePersistenceOutcomeVO:
    """Unified state persistence result — input and output in one VO."""

    success: bool = False
    duration_ms: float = 0.0
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


# ============================================================
# FR-LAU-005: Load Outcome (with warnings)
# ============================================================


@dataclass(frozen=True)
class LoadOutcomeVO:
    """FR-LAU-005 load result with corruption/parse warnings."""

    state: RuntimeStateVO | None = None
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    corrupted: bool = False


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
