"""Telemetry domain contract: event enrichment protocol (ABC based).

FR-TLM-004: Enrich Events with Environment Metadata
Attaches coarse, version-level environment context to outgoing batches.
No identifying information included.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    BlenderVersion,
    PlatformName,
    VersionString,
)


class TelemetryEnrichmentProtocol(ABC):
    """Async protocol for enriching telemetry events with environment metadata."""

    @abstractmethod
    async def enrich_event(
        self,
        event: dict[str, Any],
        platform: PlatformName | None = None,
        version: VersionString | None = None,
    ) -> dict[str, Any]:
        """Attach coarse environment context to event.

        FR-TLM-004: Permitted fields are OS family, runtime version,
        Blender version, and application version at major/minor granularity.
        No hostname, username, path, or hardware identifier included.

        Args:
            event: The telemetry event to enrich.
            platform: Optional platform override.
            version: Optional version override.

        Returns:
            Event dict with environment metadata appended.
        """
        ...

    @abstractmethod
    async def get_environment_metadata(self) -> dict[str, Any]:
        """Return current environment snapshot for batch envelope.

        Returns:
            Dict with os_family, runtime_version, blender_version, app_version.
        """
        ...


class TelemetryEnrichmentPort(ABC):
    """Sync facade for orchestrator consumption."""

    @abstractmethod
    def enrich_event_metadata(self) -> dict[str, Any]:
        """Gather and attach environment metadata to events.

        FR-TLM-004: Attach application version, operating system type,
        and 3D application version to events. Missing fields default to "unknown".
        No sensitive file paths, user-specific directory names, or machine hostnames.
        """
        ...

    @abstractmethod
    def get_app_version(self) -> VersionString:
        """Return the application version string."""
        ...

    @abstractmethod
    def get_platform(self) -> PlatformName:
        """Return the platform name (e.g., 'linux', 'darwin', 'win32')."""
        ...

    @abstractmethod
    def get_blender_version(self) -> BlenderVersion | None:
        """Return the Blender version if available, None otherwise."""
        ...
