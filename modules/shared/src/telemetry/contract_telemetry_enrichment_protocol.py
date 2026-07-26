"""Telemetry domain contract: event enrichment protocol (ABC based).

Defines the protocol for attaching coarse, version-level environment
context to outgoing batches. No identifying information.

FR-TLM-004: Enrich Events with Environment Metadata
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TelemetryEnrichmentProtocol(ABC):
    """Protocol for enriching telemetry events with environment metadata."""

    @abstractmethod
    async def enrich_event(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """Attach coarse environment context to event.

        FR-TLM-004: Permitted fields are OS family, runtime version,
        Blender version, and application version at major/minor granularity.
        No hostname, username, path, or hardware identifier included.

        Args:
            event: The telemetry event to enrich.

        Returns:
            Event dict with environment metadata appended.
        """
        pass

    @abstractmethod
    async def get_environment_metadata(self) -> dict[str, Any]:
        """Return current environment snapshot for batch envelope.

        Returns:
            Dict with os_family, runtime_version, blender_version, app_version.
        """
        pass