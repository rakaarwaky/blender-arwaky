"""Telemetry domain contract: event enrichment protocol (ABC based).

FR-TLM-004: Enrich Events with Environment Metadata
Attaches coarse, version-level environment context to outgoing batches.
No identifying information included.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.telemetry.taxonomy_telemetry_event import EnvironmentMetadata


class TelemetryEnrichmentProtocol(ABC):
    """Sync protocol for enriching telemetry events with environment metadata."""

    @abstractmethod
    def get_environment_metadata(self) -> EnvironmentMetadata:
        """Return current environment snapshot.

        FR-TLM-004: Permitted fields are OS family, runtime version,
        Blender version, and application version at major/minor granularity.
        No hostname, username, path, or hardware identifier included.

        Returns:
            EnvironmentMetadata VO with coarse environment context.
        """
        ...
