"""Telemetry domain contract: event enrichment protocol (ABC based).

Defines the protocol for attaching coarse, version-level environment
context to outgoing batches. No identifying information.

FR-TLM-004: Enrich Events with Environment Metadata
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import Details, PlatformName, VersionString


class TelemetryEnrichmentProtocol(ABC):
    """Protocol for enriching telemetry events with environment metadata."""

    @abstractmethod
    async def enrich_event(
        self,
        event: dict[str, Any],
        platform: PlatformName | None = None,
        version: VersionString | None = None,
    ) -> Details:
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
    async def get_environment_metadata(self) -> Details:
        """Return current environment snapshot for batch envelope.

        Returns:
            Dict with os_family, runtime_version, blender_version, app_version.
        """
        pass

# --- Merged from contract_telemetry_enrichment.py ---

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
