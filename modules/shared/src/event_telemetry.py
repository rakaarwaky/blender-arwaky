"""Telemetry event data structure."""

from __future__ import annotations

from dataclasses import dataclass, field

from .constant_core_types import (
    BlenderVersion,
    CustomerUuid,
    Details,
    DurationMs,
    ErrorString,
    PlatformName,
    Prompt,
    SessionId,
    SuccessFlag,
    Timestamp,
    ToolName,
    VersionString,
)
from .constant_event_type import EventType


@dataclass
class TelemetryEvent:
    """Structure for telemetry events."""

    event_type: EventType
    customer_uuid: CustomerUuid
    session_id: SessionId
    timestamp: Timestamp
    version: VersionString
    platform: PlatformName
    tool_name: ToolName | None = None
    prompt_text: Prompt | None = None
    success: SuccessFlag = SuccessFlag(True)
    duration_ms: DurationMs | None = None
    error_message: ErrorString | None = None
    blender_version: BlenderVersion | None = None
    metadata: Details | None = None
