"""Contract: Config aggregate facade.

Unified interface for the config feature consumed by the Surface layer.
Combines settings loading, retrieval, workspace resolution, metadata, and
redaction into a single entry point.

Implemented by Agent layer (ConfigOrchestrator).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from .taxonomy_config_constant import EVENT_RING_BUFFER_SIZE
from .taxonomy_config_vo import (
    DEFAULT_CONFIG_FLOAT,
    DEFAULT_CONFIG_INT,
    DEFAULT_CONFIG_STRING,
    ConfigEventLimit,
    ConfigFloatValue,
    ConfigIntValue,
    ConfigStringValue,
    EventPayload,
    RedactionRule,
    SettingsData,
    SettingsOverrides,
    SettingsSnapshot,
    SettingsValue,
    WorkspacePath,
)

DEFAULT_CONFIG_EVENT_LIMIT: ConfigEventLimit = ConfigEventLimit(EVENT_RING_BUFFER_SIZE)


class IConfigAggregate(ABC):
    """Aggregate facade for the config feature.

    Surface layer delegates all config operations through this interface.
    """

    # ─── Lifecycle ──────────────────────────────────────────────

    @abstractmethod
    def load(
        self,
        path: ConfigPath | None = None,
        overrides: SettingsOverrides | None = None,
    ) -> SettingsSnapshot:
        """Load settings and return immutable snapshot."""
        ...

    @abstractmethod
    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached settings snapshot."""
        ...

    @abstractmethod
    def get_snapshot(self) -> SettingsSnapshot:
        """Return current cached settings snapshot (lazy-loads if needed)."""
        ...

    # ─── Retrieval (FR-CFG-002) ────────────────────────────────

    @abstractmethod
    def get(self, path: ConfigPath = "", default: SettingsValue = None) -> SettingsValue:
        """Retrieve value by dot-separated path from current snapshot."""
        ...

    @abstractmethod
    def set_config(self, path: ConfigPath, value: SettingsValue) -> SettingsSnapshot:
        """Atomically persist a typed value and return the new snapshot."""
        ...

    @abstractmethod
    def has(self, path: ConfigPath) -> bool:
        """Check if a dot-separated path exists in the current snapshot."""
        ...

    @abstractmethod
    def get_string(self, path: ConfigPath, default: ConfigStringValue = DEFAULT_CONFIG_STRING) -> ConfigStringValue:
        """Retrieve string value."""
        ...

    @abstractmethod
    def get_int(self, path: ConfigPath, default: ConfigIntValue = DEFAULT_CONFIG_INT) -> ConfigIntValue:
        """Retrieve integer value."""
        ...

    @abstractmethod
    def get_bool(self, path: ConfigPath, default: bool = False) -> bool:
        """Retrieve boolean value."""
        ...

    @abstractmethod
    def get_float(self, path: ConfigPath, default: ConfigFloatValue = DEFAULT_CONFIG_FLOAT) -> ConfigFloatValue:
        """Retrieve float value."""
        ...

    # ─── Workspace (FR-CFG-003) ────────────────────────────────

    @abstractmethod
    def resolve_workspace(self) -> WorkspacePath:
        """Resolve project workspace directory."""
        ...

    # ─── Metadata (FR-CFG-004) ────────────────────────────────

    @abstractmethod
    def get_metadata(self) -> ConfigMetadata | None:
        """Return settings loading metadata (secrets excluded)."""
        ...

    # ─── Events (T-09) ─────────────────────────────────────────

    @abstractmethod
    def recent_events(
        self,
        limit: ConfigEventLimit = DEFAULT_CONFIG_EVENT_LIMIT,
    ) -> tuple[EventPayload, ...]:
        """Return recent config domain events, oldest → newest."""
        ...

    # ─── Redaction (FR-CFG-005) ────────────────────────────────

    @abstractmethod
    def get_redaction_rule(self) -> RedactionRule:
        """Return authoritative redaction rule."""
        ...

    @abstractmethod
    def redact_dict(self, data: SettingsData) -> SettingsData:
        """Recursively redact sensitive values in a dictionary."""
        ...
