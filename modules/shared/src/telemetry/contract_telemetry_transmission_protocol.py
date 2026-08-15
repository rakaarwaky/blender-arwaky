"""Telemetry transmission boundary.

The domain may prepare batches for transmission, but transport ownership remains
outside telemetry until a supported endpoint is configured.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from modules.shared.src.telemetry.taxonomy_telemetry_event import TelemetryRecord


class TelemetryTransmissionProtocol(ABC):
    """Port for transmitting already-scrubbed telemetry records."""

    @abstractmethod
    def transmit(self, records: Sequence[TelemetryRecord]) -> bool:
        """Transmit a batch and return whether the boundary acknowledged it."""
        raise NotImplementedError
