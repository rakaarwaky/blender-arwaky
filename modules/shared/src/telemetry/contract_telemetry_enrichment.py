"""Contract: Telemetry enrichment port interface.

Defines the contract for enriching telemetry events with environment metadata.
AES Port layer — depends only on taxonomy entities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import (
    BlenderVersion,
    Details,
    PlatformName,
    VersionString,
)


class TelemetryEnrichmentPort(ABC):
    """Port interface for telemetry event enrichment with environment metadata."""

    @abstractmethod
    def enrich_event_metadata(self) -> Details:
        """Gather and attach environment metadata to events.

        FR-TLM-004: Attach application version, operating system type,
        and 3D application version to events. Missing fields default to "unknown".
        No sensitive file paths, user-specific directory names, or machine hostnames.
        """
        pass

    @abstractmethod
    def get_app_version(self) -> VersionString:
        """Return the application version string."""
        pass

    @abstractmethod
    def get_platform(self) -> PlatformName:
        """Return the platform name (e.g., 'linux', 'darwin', 'win32')."""
        pass

    @abstractmethod
    def get_blender_version(self) -> BlenderVersion | None:
        """Return the Blender version if available, None otherwise."""
        pass
