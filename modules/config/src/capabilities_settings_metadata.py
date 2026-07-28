"""Capability: Settings metadata provider (FR-CFG-004).

Implements ISettingsMetadataProtocol — exposes diagnostic metadata
about settings loading without leaking secrets.
"""

from __future__ import annotations

from collections.abc import Callable

from modules.shared.src.config.taxonomy_config_vo import EventPayload

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsMetadataCapability(ISettingsMetadataProtocol):
    """FR-CFG-004: Provide settings metadata.

    Exposes source, override count, warnings, policy mode, and timestamps.
    Must never include secret values or raw settings content.

    The metadata supplier is a bound method (e.g. loader.get_last_metadata)
    wired by the composition root — no capability-to-capability imports.
    """

    def __init__(self, metadata_supplier: Callable[[], ConfigMetadata] | None = None) -> None:
        self._metadata_supplier = metadata_supplier

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_metadata(self) -> ConfigMetadata:
        """Return current settings metadata (reflects latest load/reload)."""
        if self._metadata_supplier is None:
            return ConfigMetadata()
        return self._metadata_supplier()

    def to_safe_dict(self, metadata: ConfigMetadata) -> EventPayload:
        """Serialize metadata for diagnostics output (secrets excluded)."""
        return metadata.to_dict()

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "SettingsMetadataCapability()"
