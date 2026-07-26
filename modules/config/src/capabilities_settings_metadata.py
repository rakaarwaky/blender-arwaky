"""Capability: Settings metadata provider (FR-CFG-004).

Implements ISettingsMetadataProtocol — exposes diagnostic metadata
about settings loading without leaking secrets.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol


class SettingsMetadataCapability(ISettingsMetadataProtocol):
    """FR-CFG-004: Provide settings metadata.

    Exposes source, override count, warnings, policy mode, and timestamps.
    Must never include secret values or raw settings content.
    """

    def __init__(self, metadata: ConfigMetadata | None = None) -> None:
        self._metadata = metadata

    def get_metadata(self) -> ConfigMetadata:
        """Return current settings metadata."""
        if self._metadata is None:
            return ConfigMetadata()
        return self._metadata

    def to_safe_dict(self, metadata: ConfigMetadata) -> dict[str, Any]:
        """Serialize metadata for diagnostics output.

        Safe for CLI, MCP-facing responses, and logging.
        Secrets excluded by design — metadata must never contain them.
        """
        return {
            "source": metadata.source,
            "exists": metadata.exists,
            "overrides": metadata.overrides,
            "parse_warnings": metadata.parse_warnings,
            "validation_warnings": metadata.validation_warnings,
        }
