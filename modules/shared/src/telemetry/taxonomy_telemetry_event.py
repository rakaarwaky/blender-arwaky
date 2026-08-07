"""Telemetry event taxonomy — PII-free event types and allowlists.

FRD hard rule: Never store customer_uuid, error messages, prompts, or
user-identifiable content in telemetry records.

FR-TLM-001: Allowlist of action types that may be recorded.
FR-TLM-002: Feature area taxonomy mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    BlenderVersion,
    PlatformName,
    SessionId,
    SuccessFlag,
    Timestamp,
    VersionString,
)

FeatureArea = NewType("FeatureArea", str)
OperationType = NewType("OperationType", str)
OutcomeCategory = NewType("OutcomeCategory", str)
DurationBucket = NewType("DurationBucket", float)
OsFamily = NewType("OsFamily", str)
RuntimeVersion = NewType("RuntimeVersion", str)
SchemaVersion = NewType("SchemaVersion", str)
TelemetryErrorCategory = NewType("TelemetryErrorCategory", str)


class TelemetryCategory(Enum):
    """Fixed low-cardinality telemetry categories (FR-TLM-002)."""

    STARTUP = "startup"
    TOOL_EXECUTION = "tool_execution"
    PROMPT_SENT = "prompt_sent"
    CONNECTION = "connection"
    ERROR = "error"
    OTHER = "other"


class TelemetryRejectionReason(Enum):
    """Reasons a telemetry record can be rejected."""

    CONSENT_INACTIVE = "consent_inactive"
    ACTION_NOT_ALLOWLISTED = "action_not_allowlisted"
    INVALID_RECORD = "invalid_record"


@dataclass(frozen=True)
class ClassificationResult:
    """Result of event classification with fixed taxonomy values."""

    category: TelemetryCategory
    feature_area: FeatureArea
    operation_type: OperationType
    outcome_category: OutcomeCategory


@dataclass(frozen=True)
class EnvironmentMetadata:
    """Coarse environment metadata with no PII (FR-TLM-004)."""

    app_version: VersionString
    platform: PlatformName
    blender_version: BlenderVersion | None
    os_family: OsFamily
    runtime_version: RuntimeVersion
    schema_version: SchemaVersion


@dataclass(frozen=True)
class TelemetryDraft:
    """Composed draft ready for recording (agent-assembled, PII-free)."""

    action_type: ActionName
    classification: ClassificationResult
    session_id: SessionId
    outcome_category: OutcomeCategory
    duration_bucket: DurationBucket | None = None


@dataclass(frozen=True)
class TelemetryRecord:
    """Immutable buffered telemetry record with full snapshot."""

    action_type: ActionName
    category: TelemetryCategory
    session_id: SessionId
    timestamp: Timestamp
    feature_area: FeatureArea
    operation_type: OperationType
    outcome_category: OutcomeCategory
    version: VersionString
    platform: PlatformName
    duration_bucket: DurationBucket | None = None


@dataclass(frozen=True)
class RecordingResult:
    """Result of a recording attempt."""

    recorded: SuccessFlag
    rejection_reason: TelemetryRejectionReason | None = None


@dataclass(frozen=True)
class TelemetryEvent:
    """PII-free telemetry event structure.

    FRD: Never includes raw payloads, names, paths, prompts, error messages,
    or customer/user-identifiable information.

    """

    category: TelemetryCategory
    session_id: SessionId
    timestamp: Timestamp
    feature_area: FeatureArea
    operation_type: OperationType
    outcome_category: OutcomeCategory
    version: VersionString = VersionString("unknown")
    platform: PlatformName = PlatformName("unknown")
    duration_bucket: DurationBucket | None = None
    metadata: dict[str, str] | None = None
