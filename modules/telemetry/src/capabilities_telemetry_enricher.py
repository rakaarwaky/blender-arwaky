"""Capability: Telemetry event enricher.

Implements TelemetryEnrichmentProtocol — attaches coarse, version-level
environment context to outgoing batches. No identifying information.

FR-TLM-004: Enrich Events with Environment Metadata
"""

from __future__ import annotations

import platform
import subprocess
import sys
from typing import Any

from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import TelemetryEnrichmentProtocol


class TelemetryEnrichmentCapability(TelemetryEnrichmentProtocol):
    """Business logic for enriching telemetry events with environment metadata."""

    def __init__(
        self,
        app_version: str = "0.1.0",
    ) -> None:
        """Initialize with application version.

        Args:
            app_version: Application version string.
        """
        self._app_version = app_version
        self._cached_metadata: dict[str, Any] | None = None

    async def enrich_event(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """Attach coarse environment context to event.

        FR-TLM-004: Permitted fields are OS family, runtime version,
        Blender version, and application version at major/minor granularity.

        Args:
            event: The telemetry event to enrich.

        Returns:
            Event dict with environment metadata appended.
        """
        metadata = await self.get_environment_metadata()
        enriched = dict(event)
        enriched["environment"] = metadata
        return enriched

    async def get_environment_metadata(self) -> dict[str, Any]:
        """Return current environment snapshot for batch envelope.

        Returns:
            Dict with os_family, runtime_version, blender_version, app_version.
        """
        if self._cached_metadata is not None:
            return self._cached_metadata

        # OS family (coarse)
        os_name = platform.system().lower()
        if os_name.startswith("linux"):
            os_family = "linux"
        elif os_name.startswith("darwin"):
            os_family = "macos"
        elif os_name.startswith("windows"):
            os_family = "windows"
        else:
            os_family = os_family = "other"

        # Runtime version (major.minor only)
        runtime_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        # Blender version (best-effort detection)
        blender_version = self._detect_blender_version() or "unknown"

        self._cached_metadata = {
            "os_family": os_family,
            "runtime_version": runtime_version,
            "blender_version": blender_version,
            "app_version": self._app_version,
        }
        return self._cached_metadata

    def _detect_blender_version(self) -> str | None:
        """Detect Blender version via subprocess (best-effort, non-blocking)."""
        try:
            result = subprocess.run(
                ["blender", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # Parse "Blender 3.6.0 (Linux 12.4.3 x64 ...)"
                parts = result.stdout.strip().split()
                for part in parts:
                    if "." in part and part[0].isdigit():
                        return part
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return None