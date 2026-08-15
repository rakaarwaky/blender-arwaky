"""Telemetry transmission boundary implementation.

No network transport is enabled by default. A caller may inject a sender when a
supported transport is configured; failures are contained at this boundary.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from modules.shared.src.telemetry.taxonomy_telemetry_event import TelemetryRecord

logger = logging.getLogger("blender-arwaky.telemetry")


@dataclass(frozen=True)
class TelemetryTransmissionResult:
    """Acknowledgment from the transmission boundary."""

    transmitted: bool
    attempted: bool
    error: str | None = None


class TelemetryTransmissionCapability:
    """Transmit scrubbed records only through an explicitly injected sender."""

    def __init__(
        self,
        sender: Callable[[Sequence[TelemetryRecord]], None] | None = None,
    ) -> None:
        self._sender = sender

    def transmit(self, records: Sequence[TelemetryRecord]) -> TelemetryTransmissionResult:
        """Attempt a batch transmission without leaking record contents in errors."""
        if not records:
            return TelemetryTransmissionResult(transmitted=True, attempted=False)
        if self._sender is None:
            return TelemetryTransmissionResult(
                transmitted=False,
                attempted=False,
                error="transmission_not_configured",
            )
        try:
            self._sender(records)
        except Exception:
            logger.exception("Telemetry transmission failed")
            return TelemetryTransmissionResult(
                transmitted=False,
                attempted=True,
                error="transmission_failed",
            )
        return TelemetryTransmissionResult(transmitted=True, attempted=True)
