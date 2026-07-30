"""Capability: Telemetry event enricher.

Implements TelemetryEnrichmentProtocol — handles gathering and attaching
environment metadata to telemetry events per FR-TLM-004.
"""

from __future__ import annotations

import logging
import platform
import threading

from modules.shared.src.common.taxonomy_core_vo import (
    BlenderVersion,
    PlatformName,
    VersionString,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    EnvironmentMetadata,
    OsFamily,
    RuntimeVersion,
    SchemaVersion,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryEventEnricher(TelemetryEnrichmentProtocol):
    def __init__(self, app_version: VersionString | None = None) -> None:
        self._cache: EnvironmentMetadata | None = None
        self._lock = threading.Lock()
        self._app_version = app_version

    def get_environment_metadata(self) -> EnvironmentMetadata:
        with self._lock:
            if self._cache is not None:
                return self._cache

            metadata = EnvironmentMetadata(
                app_version=self._app_version or VersionString("unknown"),
                platform=self._get_platform(),
                blender_version=self._get_blender_version(),
                os_family=self._get_os_family(),
                runtime_version=self._get_runtime_version(),
                schema_version=SchemaVersion("1.0"),
            )
            self._cache = metadata
            return metadata

    def _get_platform(self) -> PlatformName:
        try:
            return PlatformName(platform.system().lower())
        except Exception:
            return PlatformName("unknown")

    def _get_os_family(self) -> OsFamily:
        try:
            return OsFamily(platform.system().lower())
        except Exception:
            return OsFamily("unknown")

    def _get_runtime_version(self) -> RuntimeVersion:
        try:
            major, minor, _ = platform.python_version_tuple()
            return RuntimeVersion(f"{major}.{minor}")
        except Exception:
            return RuntimeVersion("unknown")

    def _get_blender_version(self) -> BlenderVersion | None:
        return None
