"""Contract: Settings loader protocol (FR-CFG-001).

Defines the inbound behavior interface for loading, validating,
and reloading application settings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from .taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
)
from .taxonomy_config_vo import SettingsSnapshot


class ISettingsLoaderProtocol(ABC):
    """Protocol for loading and applying settings (FR-CFG-001)."""

    @abstractmethod
    def load_settings(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings from all sources, apply precedence, validate, return immutable snapshot."""
        ...

    @abstractmethod
    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous valid snapshot on failure (permissive)."""
        ...

    @abstractmethod
    def get_last_metadata(self) -> ConfigMetadata:
        """Return metadata from the most recent successful load."""
        ...

    @abstractmethod
    def emit_loaded_event(self) -> SettingsLoadedEvent:
        """Build a settings-loaded event payload from the most recent load metadata."""
        ...

    @abstractmethod
    def emit_reload_event(self) -> SettingsReloadEvent:
        """Build a settings-reload event payload from the most recent load metadata."""
        ...

    @abstractmethod
    def emit_validation_warning_event(self) -> SettingsValidationWarningEvent | None:
        """Return warning event when permissive-mode warnings exist, else None."""
        ...