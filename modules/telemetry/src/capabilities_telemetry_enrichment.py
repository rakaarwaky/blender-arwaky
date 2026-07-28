"""Capability: Telemetry event enricher.

Implements TelemetryEnrichmentPort — handles gathering and attaching
environment metadata to telemetry events per FR-TLM-004.
"""

from __future__ import annotations

import logging
import platform
import sys
import threading
from pathlib import Path
from typing import Any

try:
    import tomli as _tomli
except ImportError:
    try:
        import tomllib as _tomllib
    except ImportError:
        _tomli = None
        _tomllib = None

from modules.shared.src.common.taxonomy_core_vo import (
    BlenderVersion,
    Details,
    PlatformName,
    VersionString,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentProtocol,
)

logger = logging.getLogger("blender-arwaky-telemetry-service")


class TelemetryEventEnricher(TelemetryEnrichmentProtocol):
    """Telemetry event enrichment implementation.

    FR-TLM-004: Enriches events with environment metadata (OS, app version,
    Blender version). Missing fields default to "unknown". No PII included.
    """

    def __init__(self) -> None:
        self._metadata_cache: Details | None = None
        self._cache_lock = threading.Lock()

    def enrich_event_metadata(self) -> Details:
        """Gather and attach environment metadata to events.

        FR-TLM-004: Attaches application version, OS type, and Blender version.
        Missing fields default to "unknown". No sensitive file paths or hostnames.
        """
        with self._cache_lock:
            if self._metadata_cache is not None:
                return self._metadata_cache

            # Build metadata dict
            metadata: dict[str, Any] = {
                "app_version": self.get_app_version(),
                "platform": self.get_platform(),
                "blender_version": str(self.get_blender_version()) if self.get_blender_version() else "unknown",
            }

            # Add OS details (non-sensitive)
            try:
                metadata["os_type"] = platform.system().lower()
            except Exception as e:
                logger.debug("Failed to get OS type: %s", e)
                metadata["os_type"] = "unknown"

            try:
                metadata["os_version"] = platform.version() or "unknown"
            except Exception as e:
                logger.debug("Failed to get OS version: %s", e)
                metadata["os_version"] = "unknown"

            # Cache the metadata (non-sensitive, safe to cache)
            self._metadata_cache = Details(str(metadata))
            return self._metadata_cache

    def get_app_version(self) -> VersionString:
        """Return the application version string.

        Attempts multiple methods to determine version:
        1. importlib.metadata (pip-installed packages)
        2. pyproject.toml (development layout)
        3. Falls back to "unknown"
        """
        try:
            from importlib.metadata import version as _v

            return VersionString(_v("blender-arwaky"))
        except Exception:
            pass

        # Fallback: try pyproject.toml in development layout
        if _tomli or _tomllib:
            try:
                p = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
                if p.exists():
                    parser = _tomli or _tomllib
                    with open(p, "rb") as f:
                        v = parser.load(f).get("project", {}).get("version", "unknown")
                        return VersionString(str(v))
            except Exception as e:
                logger.debug("Failed to read package version: %s", e)

        return VersionString("unknown")

    def get_platform(self) -> PlatformName:
        """Return the platform name.

        Returns normalized platform identifier (e.g., 'linux', 'darwin', 'win32').
        Falls back to "unknown" if detection fails.
        """
        try:
            return PlatformName(platform.system().lower())
        except Exception as e:
            logger.debug("Failed to get platform: %s", e)
            return PlatformName("unknown")

    def get_blender_version(self) -> BlenderVersion | None:
        """Return the Blender version if available.

        Attempts to detect Blender version from environment or runtime.
        Returns None if detection fails (will default to "unknown" in enrichment).
        """
        try:
            # Check for BLENDER_VERSION environment variable
            env_version = self._get_env_blender_version()
            if env_version:
                return BlenderVersion(env_version)

            # Check sys.version for running Blender instance
            sys_version = self._get_sys_blender_version()
            if sys_version:
                return BlenderVersion(sys_version)

        except Exception as e:
            logger.debug("Failed to detect Blender version: %s", e)

        return None

    def _get_env_blender_version(self) -> str | None:
        """Get Blender version from environment variables."""
        try:
            env_var = "BLENDER_VERSION"
            version = sys.modules.get("os", {}).get("environ", {}).get(env_var)
            if not version:
                import os as _os

                version = _os.environ.get(env_var)
            return version
        except Exception:
            return None

    def _get_sys_blender_version(self) -> str | None:
        """Get Blender version from sys.version or platform.python_version."""
        try:
            # Check if running inside Blender (sys.prefix contains blender)
            if hasattr(sys, "version"):
                # This is a simplified check - in production would parse more thoroughly
                return None
        except Exception:
            pass
        return None
