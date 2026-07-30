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
# FRD Error Categories (machine-readable, traceable)
# ============================================================


class LauncherErrorCode(str, Enum):
    """Machine-readable error codes mapped to FRD error categories."""

    CONFIGURATION_ERROR = "configuration_error"  # config / executable path error
    TIMEOUT_ERROR = "timeout_error"  # timeout on launch/shutdown
    VALIDATION_ERROR = "validation_error"  # validation failure
    STATE_ERROR = "state_error"  # invalid runtime state
    LAUNCH_ERROR = "launch_error"  # spawn/execution failure
    TERMINATION_ERROR = "termination_error"  # shutdown/kill failure
    PERSISTENCE_ERROR = "persistence_error"  # persistence failure
    UNKNOWN = "unknown"  # unclassified error


# ============================================================
# Bridge Endpoint (FR-LAU-002 / P0: Shared endpoint VO)
# ============================================================


@dataclass(frozen=True)
class BridgeEndpointVO:
    """Shared bridge endpoint — single source for Gateway connection config.

    P0: Eliminates str | None bridge_endpoint across Launcher/Gateway.
    """

    host: str = "localhost"
    port: int = 9876
    protocol_version: str = "2.0.0"


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
    """Unified registration result — input and output in one VO.

    FRD error categories are now machine-readable via error_code.
    """

    executable: ExecutableReferenceVO | None = None
    source: RegistrationSource | None = None
    registered: bool = False
    warning: str | None = None
    error: str | None = None
    error_code: LauncherErrorCode | None = None


# ============================================================
# FR-LAU-002: Launch Request / Outcome
# ============================================================


@dataclass(frozen=True)
class LaunchRequestVO:
    """Launch request containing mode, readiness timeout, and bridge endpoint settings.

    FR-LAU-002: Input includes "bridge endpoint settings" — this VO provides
    a contract-level way to pass endpoint host/port/protocol information.
    """

    mode: LaunchMode = LaunchMode.INTERFACE
    readiness_timeout_seconds: TimeoutSeconds | None = None
    bridge_endpoint: BridgeEndpointVO | None = None


@dataclass(frozen=True)
class LaunchOutcomeVO:
    """Unified launch result — input and output in one VO."""

    success: bool = False
    process_id: int | None = None
    ready: bool = False
    bridge_endpoint: BridgeEndpointVO | None = None
    duration_ms: float = 0.0
    launch_method: LaunchMethod = LaunchMethod.SPAWN
    error: str | None = None
    error_code: LauncherErrorCode | None = None


# ============================================================
# FR-LAU-003: Shut Down
# ============================================================


@dataclass(frozen=True)
class ShutdownRequestVO:
    """FR-LAU-003 shutdown input with explicit force/escalation confirmation semantics.

    Replaces ambiguous force/allow_escalation booleans with a single request VO.
    """

    force_requested: bool = False
    escalation_confirmed: bool = True


@dataclass(frozen=True)
class ShutdownOutcomeVO:
    """Unified shutdown result — input and output in one VO."""

    success: bool = False
    termination_method: TerminationMethod = TerminationMethod.NONE
    duration_ms: float = 0.0
    final_state: RuntimeState = RuntimeState.NOT_RUNNING
    escalated: bool = False
    error: str | None = None
    error_code: LauncherErrorCode | None = None


# ============================================================
# FR-LAU-004: Runtime Status
# ============================================================


@dataclass(frozen=True)
class RuntimeStatusVO:
    """Unified runtime status — input and output in one VO.

    FRD FR-LAU-004 requires process ref summary, readiness, staleness, uptime.
    Additional metadata fields added for diagnostics integration.
    """

    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    ready: bool = False
    stale: bool = False
    uptime_seconds: float | None = None
    depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT
    # Additional diagnostics metadata (secrets redacted)
    process_reference: str = ""
    bridge_endpoint_summary: str = ""
    probe_duration_ms: float = 0.0
    classification_reason: str = ""


@dataclass(frozen=True)
class StatusCheckOutcomeVO:
    """Unified runtime status check result — input and output in one VO."""

    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    bridge_endpoint: BridgeEndpointVO | None = None
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
    bridge_endpoint: BridgeEndpointVO | None = None
    last_status: RuntimeState = RuntimeState.NOT_RUNNING


@dataclass(frozen=True)
class PersistenceOutcomeVO:
    """Unified persistence result — input and output in one VO."""

    success: bool = False
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    reconciled: bool = False


@dataclass(frozen=True)
class LoadOutcomeVO:
    """FR-LAU-005 load result with warnings.

    Replaces silent load failures with explicit warning emission.
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
    bridge_endpoint: str | None = None
    addon_path: str | None = None
