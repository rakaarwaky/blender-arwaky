"""Agent: Telemetry feature orchestrator.

Coordinates telemetry event recording and session tracking.
"""

import logging
from typing import Any

from modules.shared.src.telemetry.contract_telemetry_recording import TelemetryRecordingPort
from modules.shared.src.telemetry.taxonomy_telemetry_event import EventType, TelemetryEvent

logger = logging.getLogger("BlenderMCPServer")


class TelemetryOrchestrator:
    """Orchestrates telemetry operations."""

    def __init__(self, recorder: TelemetryRecordingPort):
        self._recorder = recorder

    async def record_event(self, event: TelemetryEvent) -> None:
        """Record a telemetry event."""
        await self._recorder.record(event)

    def start_session(self) -> str:
        """Start a new telemetry session."""
        return self._recorder.start_session()
