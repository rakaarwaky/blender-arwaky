"""Diagnostics domain — Value Objects for health, metrics, audit, and snapshots.

Frozen dataclasses with explicit types. All VOs are immutable.
Input and output fields live in a single VO per concept.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any

# ============================================================
# Health Composition (FR-DIA-001)
# ============================================================


@dataclass(frozen=True)
class SubsystemHealthVO:
    """Health status for a single subsystem."""

    name: str
    status: str  # healthy / degraded / unhealthy / unknown / stale / timeout
    staleness_delta_seconds: float = 0.0
    probe_duration_ms: float = 0.0


@dataclass(frozen=True)
class HealthDetailsVO:
    """Unified health composition — input and output in one VO.

    Callee sets overall_status, subsystems, staleness indicators, composition timestamp.
    """

    # Output
    overall_status: str = "unknown"  # healthy / degraded / unhealthy
    subsystems: tuple[SubsystemHealthVO, ...] = dc_field(default_factory=tuple)
    staleness_indicators: dict[str, float] = dc_field(default_factory=dict)
    composition_timestamp: str = ""


# ============================================================
# Metrics Collection (FR-DIA-002)
# ============================================================


@dataclass(frozen=True)
class LatencySummaryVO:
    """Latency summary with count, min, max, mean, and percentiles."""

    count: int = 0
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0


@dataclass(frozen=True)
class MetricsSnapshotVO:
    """Unified metrics collection — input and output in one VO.

    Callee sets counters, latency summaries, freshness indicators, collection timestamp.
    """

    # Output
    counters: dict[str, int] = dc_field(default_factory=dict)
    latency_summaries: dict[str, LatencySummaryVO] = dc_field(default_factory=dict)
    freshness_indicators: dict[str, str] = dc_field(default_factory=dict)
    collection_timestamp: str = ""
    counter_reset_indicator: bool = False


# ============================================================
# Audit Emission (FR-DIA-003)
# ============================================================


@dataclass(frozen=True)
class AuditRecordVO:
    """Immutable audit record — frozen once emitted.

    Correction = new record with same category + correlation_id + new timestamp.
    """

    # Input (context)
    category: str = ""
    severity: str = "info"
    source_feature: str = ""
    operation_type: str = ""
    target_metadata: dict[str, Any] = dc_field(default_factory=dict)
    correlation_id: str | None = None

    # Output (emitted event — frozen by dataclass(frozen=True))
    record_id: str = ""
    timestamp: float = 0.0
    emission_confirmed: bool = False
    emission_path: str = "direct"  # direct / fallback


# ============================================================
# Snapshot Provision (FR-DIA-005)
# ============================================================


@dataclass(frozen=True)
class AuditSummaryVO:
    """Summary of recent audit events — categories + counts only."""

    total_records: int = 0
    recent_categories: tuple[str, ...] = dc_field(default_factory=tuple)
    category_counts: dict[str, int] = dc_field(default_factory=dict)


@dataclass(frozen=True)
class DiagnosticsSnapshotVO:
    """Unified diagnostics snapshot — point-in-time view.

    Composed from health, metrics, audit summary, and config metadata.
    CLI/MCP consume this — never probe subsystems or compute health themselves.
    """

    # Sections (all optional — filtered by consumer)
    health: HealthDetailsVO | None = None
    metrics: MetricsSnapshotVO | None = None
    audit_summary: AuditSummaryVO | None = None
    config_valid: bool = False
    system_version: str = ""
    protocol_version: str = ""
    detail_level: str = "summary"  # summary / full
    staleness_indicators: dict[str, str] = dc_field(default_factory=dict)
    first_run_indicator: bool = False


# ============================================================
# Logging (FR-DIA-004) — return confirmation VO
# ============================================================


@dataclass(frozen=True)
class LogResultVO:
    """Logging confirmation — destination metadata after redaction."""

    logged: bool = True
    destination: str = "buffer"  # buffer / file / stream / fallback
    redacted_count: int = 0
    drop_counter: int = 0  # records dropped due to backpressure
